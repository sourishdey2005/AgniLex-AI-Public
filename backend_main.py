from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import os
from dotenv import load_dotenv
import logging

# Import modules
from backend_models import (
    User, Conversation, Message, Document, Analytics, WorkflowLog,
    init_db, get_db
)
from backend_auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_admin
)
from backend_chat import ChatManager, analyze_sentiment, categorize_query, detect_escalation
from backend_rag import RAGPipeline, process_document, chunk_text

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

app = FastAPI(title="Customer Support AI Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs("./uploads", exist_ok=True)
os.makedirs("./logs", exist_ok=True)

# Pydantic models
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class UpdateConversationRequest(BaseModel):
    title: str

class ChatResponse(BaseModel):
    id: int
    conversation_id: int
    sender: str
    content: str
    timestamp: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: str

# ==================== Authentication Routes ====================

@app.post("/api/auth/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """User signup"""
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User created successfully", "user_id": user.id}


@app.post("/api/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login"""
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


@app.post("/api/auth/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords don't match")
    
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    user = db.query(User).filter(User.id == current_user.get("user_id")).first()
    
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    user.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@app.get("/api/auth/me")
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user info"""
    user = db.query(User).filter(User.id == current_user.get("user_id")).first()
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

# ==================== Chat Routes ====================

@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message and get AI response"""
    user_id = current_user.get("user_id")
    
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            ).first()
        else:
            conversation = Conversation(user_id=user_id, title="New Chat")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            sender="user",
            content=request.message
        )
        db.add(user_msg)
        db.commit()
        
        # Get RAG context
        rag = RAGPipeline(user_id)
        search_results = rag.search(request.message, k=3)
        rag_context = "\n".join([result[0] for result in search_results]) if search_results else None
        
        # Get chat response
        chat_manager = ChatManager(user_id, conversation.id)
        
        # Load conversation history
        history = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).all()
        chat_manager.load_history([{
            "sender": msg.sender,
            "content": msg.content
        } for msg in history])
        
        # Get AI response
        ai_response = await chat_manager.chat_with_rag(request.message, rag_context)
        
        # Save assistant message
        asst_msg = Message(
            conversation_id=conversation.id,
            sender="assistant",
            content=ai_response
        )
        db.add(asst_msg)
        
        # Update analytics
        sentiment = analyze_sentiment(request.message)
        category = categorize_query(request.message)
        escalation = detect_escalation(request.message)
        
        analytics = db.query(Analytics).filter(Analytics.user_id == user_id).first()
        if analytics:
            analytics.query_count += 1
            analytics.sentiment = sentiment
        else:
            analytics = Analytics(user_id=user_id, query_count=1, sentiment=sentiment)
            db.add(analytics)
        
        # Log workflow
        log = WorkflowLog(
            user_id=user_id,
            workflow_type="chat",
            status="success",
            details=f"Category: {category}, Escalation: {escalation}"
        )
        db.add(log)
        db.commit()
        
        return {
            "conversation_id": conversation.id,
            "user_message": request.message,
            "ai_response": ai_response,
            "sentiment": sentiment,
            "category": category,
            "needs_escalation": escalation,
            "sources": [{"text": r[0][:100]} for r in search_results[:2]] if search_results else []
        }
    
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations")
def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.get("user_id")
    ).order_by(Conversation.created_at.desc()).all()
    
    return [{
        "id": c.id,
        "title": c.title,
        "created_at": c.created_at.isoformat(),
        "message_count": len(c.messages)
    } for c in conversations]


@app.get("/api/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.get("user_id")
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "messages": [{
            "id": m.id,
            "sender": m.sender,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in messages]
    }


@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.get("user_id")
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted"}


@app.put("/api/conversations/{conversation_id}")
def update_conversation(
    conversation_id: int,
    request: UpdateConversationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.get("user_id")
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.title = request.title[:200]
    db.commit()
    
    return {"message": "Conversation renamed", "title": conversation.title}

# ==================== File Upload Routes ====================

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process document"""
    user_id = current_user.get("user_id")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.txt', '.docx']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    try:
        # Save file
        filepath = f"./uploads/{user_id}_{file.filename}"
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Add to database
        doc = Document(
            user_id=user_id,
            filename=file.filename,
            filepath=filepath,
            file_type=file_ext[1:],
            status="processing"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Process document
        text = process_document(filepath, file.filename)
        chunks = chunk_text(text)
        
        # Add to RAG
        rag = RAGPipeline(user_id)
        rag.add_documents(chunks, source=file.filename)
        
        # Update document status
        doc.status = "completed"
        db.commit()
        
        return {
            "document_id": doc.id,
            "filename": file.filename,
            "chunks_created": len(chunks),
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
def get_documents(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's documents"""
    documents = db.query(Document).filter(
        Document.user_id == current_user.get("user_id")
    ).all()
    
    return [{
        "id": d.id,
        "filename": d.filename,
        "file_type": d.file_type,
        "status": d.status,
        "uploaded_at": d.uploaded_at.isoformat()
    } for d in documents]


@app.delete("/api/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.get("user_id")
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    if os.path.exists(doc.filepath):
        os.remove(doc.filepath)
    
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted"}


@app.get("/api/documents/{document_id}/download")
def download_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download document"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.get("user_id")
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(doc.filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=doc.filepath,
        filename=doc.filename,
        media_type='application/octet-stream'
    )

# ==================== Analytics Routes ====================

@app.get("/api/analytics")
def get_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user analytics"""
    user_id = current_user.get("user_id")
    
    analytics = db.query(Analytics).filter(Analytics.user_id == user_id).first()
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
    documents = db.query(Document).filter(Document.user_id == user_id).all()
    
    return {
        "total_queries": analytics.query_count if analytics else 0,
        "average_latency": analytics.average_latency if analytics else 0,
        "sentiment": analytics.sentiment if analytics else "neutral",
        "total_conversations": len(conversations),
        "total_documents": len(documents),
        "active": True
    }

# ==================== Admin Routes ====================

@app.get("/api/admin/users")
def get_all_users(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat()
    } for u in users]


@app.delete("/api/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete RAG data
    rag = RAGPipeline(user_id)
    rag.delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted"}


@app.get("/api/admin/statistics")
def get_statistics(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics (admin only)"""
    total_users = db.query(User).count()
    total_conversations = db.query(Conversation).count()
    total_documents = db.query(Document).count()
    total_messages = db.query(Message).count()
    
    return {
        "total_users": total_users,
        "total_conversations": total_conversations,
        "total_documents": total_documents,
        "total_messages": total_messages,
        "active_users": db.query(User).filter(User.is_active == True).count()
    }


@app.get("/api/admin/workflows")
def get_workflow_logs(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all workflow logs (admin only)"""
    logs = db.query(WorkflowLog).order_by(WorkflowLog.timestamp.desc()).limit(100).all()
    
    return [{
        "id": log.id,
        "user_id": log.user_id,
        "workflow_type": log.workflow_type,
        "status": log.status,
        "timestamp": log.timestamp.isoformat()
    } for log in logs]


@app.get("/api/admin/conversations")
def get_all_conversations(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all conversations (admin only)"""
    conversations = db.query(Conversation).all()
    
    return [{
        "id": c.id,
        "user_id": c.user_id,
        "title": c.title,
        "message_count": len(c.messages),
        "created_at": c.created_at.isoformat()
    } for c in conversations]


@app.delete("/api/admin/conversations/{conversation_id}")
def admin_delete_conversation(
    conversation_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete any conversation (admin only)"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted"}


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
