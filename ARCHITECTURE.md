# 🏗️ System Architecture & Design

Complete technical architecture of the AI Customer Support Agent Platform.

---

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser                             │
│              http://localhost:8501                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   Streamlit Frontend                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  - Login/Signup Interface                           │  │
│  │  - Chat UI with Conversation History               │  │
│  │  - Document Upload                                 │  │
│  │  - Analytics Dashboard                             │  │
│  │  - Admin Dashboard (User/Conv Management)          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ REST API Calls
                             │ JSON over HTTP
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    FastAPI Backend                          │
│                 http://localhost:8000                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ API Routes:                                          │  │
│  │  - Authentication (JWT)                             │  │
│  │  - Chat & Conversations                             │  │
│  │  - Document Upload & Management                     │  │
│  │  - Analytics                                        │  │
│  │  - Admin Controls                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Services:                                            │  │
│  │  - ChatManager (LangChain)                          │  │
│  │  - RAGPipeline (Document + Search)                  │  │
│  │  - Auth (JWT + bcrypt)                              │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────┬──────────┬──────────────┬──────────┬─────────────┘
           │          │              │          │
    ┌──────▼──┐ ┌───▼─────┐ ┌───────▼──┐ ┌─────▼──────┐
    │  SQLite │ │  FAISS  │ │ LangChain│ │  OpenAI   │
    │  Database   Vector DB  Memory    API
    └─────────┘ └─────────┘ └─────────┘ └───────────┘
```

---

## 🔄 Request Flow

### Chat Request Flow

```
1. User Types Message
   │
2. Frontend sends POST /api/chat
   │
3. Backend:
   ├─ Validates JWT token
   ├─ Saves message to database
   ├─ Retrieves conversation history
   ├─ Performs RAG search (FAISS)
   ├─ Prepares context from documents
   ├─ Calls OpenAI API with context
   ├─ Analyzes sentiment
   ├─ Categorizes query
   ├─ Detects escalation
   ├─ Saves AI response
   └─ Updates analytics
   │
4. Returns response with:
   ├─ AI message
   ├─ Sentiment
   ├─ Category
   ├─ Escalation flag
   └─ Source documents
   │
5. Frontend displays message
   └─ Updates UI
```

### Document Upload Flow

```
1. User selects file
   │
2. Frontend sends multipart POST /api/upload
   │
3. Backend:
   ├─ Validates file type (PDF/DOCX/TXT)
   ├─ Saves file to ./uploads/
   ├─ Creates Document record
   ├─ Extracts text
   │  ├─ PDF: PyPDF2
   │  ├─ DOCX: python-docx
   │  └─ TXT: Read as-is
   ├─ Chunks text (500 char + 100 overlap)
   ├─ Generates embeddings (MiniLM)
   ├─ Stores in FAISS index
   ├─ Saves metadata
   └─ Updates status to "completed"
   │
4. Returns success with chunk count
   │
5. Frontend shows success message
```

### Authentication Flow

```
1. User enters credentials
   │
2. Frontend POST /api/auth/login
   │
3. Backend:
   ├─ Looks up user in database
   ├─ Verifies password with bcrypt
   ├─ Generates JWT token
   │  └─ Payload: username, user_id, role
   └─ Returns token
   │
4. Frontend stores token
   │
5. All subsequent requests include token in header
   │
6. Backend verifies token on each request
   └─ Extracts user info from token payload
```

---

## 💾 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  email VARCHAR(100) UNIQUE,
  password_hash VARCHAR(255),
  role VARCHAR(20),        -- 'user' or 'admin'
  is_active BOOLEAN,
  created_at DATETIME
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  title VARCHAR(200),
  created_at DATETIME,
  updated_at DATETIME
);
```

### Messages Table
```sql
CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  conversation_id INTEGER FOREIGN KEY,
  sender VARCHAR(20),      -- 'user' or 'assistant'
  content TEXT,
  timestamp DATETIME
);
```

### Documents Table
```sql
CREATE TABLE documents (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  filename VARCHAR(255),
  filepath VARCHAR(500),
  file_type VARCHAR(20),   -- 'pdf', 'txt', 'docx'
  uploaded_at DATETIME,
  status VARCHAR(20)       -- 'processing', 'completed', 'failed'
);
```

### Analytics Table
```sql
CREATE TABLE analytics (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  query_count INTEGER,
  average_latency FLOAT,
  sentiment VARCHAR(50),   -- 'positive', 'negative', 'neutral'
  created_at DATETIME
);
```

### WorkflowLogs Table
```sql
CREATE TABLE workflow_logs (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  workflow_type VARCHAR(100),
  status VARCHAR(50),      -- 'success', 'failed', 'pending'
  details TEXT,
  timestamp DATETIME
);
```

---

## 🤖 AI Components

### 1. LangChain ChatManager

**Purpose:** Manage conversation memory and LLM interactions

**Key Features:**
- ConversationBufferMemory for context
- ChatOpenAI for GPT-3.5-turbo
- Streaming responses
- Multi-turn conversation support

**Flow:**
```python
# Initialize with user and conversation
chat_manager = ChatManager(user_id=1, conversation_id=5)

# Load history
chat_manager.load_history(messages_list)

# Chat with RAG context
response = chat_manager.chat_with_rag(
    query="What's the warranty?",
    rag_context="Warranty details from uploaded docs"
)
```

### 2. RAG Pipeline

**Purpose:** Enable semantic search over uploaded documents

**Components:**
- Document Extraction: PDF, DOCX, TXT
- Text Chunking: 500 char chunks, 100 char overlap
- Embedding: sentence-transformers/all-MiniLM-L6-v2 (384-dim)
- Vector Storage: FAISS CPU index
- Search: L2 distance (cosine similarity)

**Flow:**
```python
# Initialize RAG for user
rag = RAGPipeline(user_id=1)

# Add documents
texts = chunk_text(extracted_text)
rag.add_documents(texts, source="document.pdf")

# Search
results = rag.search("How to reset password?", k=3)
# Returns: [(text, distance), ...]
```

### 3. Sentiment Analysis

**Purpose:** Analyze user sentiment in messages

**Method:** Keyword-based simple analysis
- Positive words: good, great, excellent, love, perfect
- Negative words: bad, terrible, awful, hate, angry
- Returns: positive, negative, or neutral

**Usage:**
```python
sentiment = analyze_sentiment("This product is amazing!")
# Returns: "positive"
```

### 4. Query Categorization

**Purpose:** Categorize user queries for analytics

**Categories:**
- `support`: Help, support, issue, problem, error
- `billing`: Price, cost, payment, billing
- `feature_inquiry`: Feature, how to, tutorial, guide
- `refund_request`: Refund, return, cancel
- `general`: Other queries

**Usage:**
```python
category = categorize_query("How much does it cost?")
# Returns: "billing"
```

### 5. Escalation Detection

**Purpose:** Identify queries needing human intervention

**Keywords:**
- urgent, critical, emergency
- legal, lawsuit
- complaint, dissatisfied, angry
- manager, supervisor, escalate

**Usage:**
```python
needs_escalation = detect_escalation("I'm furious! Need manager!")
# Returns: True
```

---

## 🔐 Security Architecture

### Password Security

```
User Input Password
    ↓
bcrypt hashing (12 rounds)
    ↓
Hash stored in database
    ↓
Login: Verify input against stored hash
    ↓
bcrypt.verify() returns True/False
```

### JWT Token Security

```
User logs in
    ↓
Generate JWT payload:
{
  "sub": "username",
  "user_id": 1,
  "role": "user",
  "exp": 1234567890
}
    ↓
Sign with SECRET_KEY using HS256
    ↓
Return token to frontend
    ↓
Frontend includes token in Authorization header
    ↓
Backend verifies token:
- Check signature
- Check expiration
- Extract user info
    ↓
Proceed with request or return 401
```

### Input Validation

```
All inputs validated by Pydantic:
- Type checking
- Length limits
- Pattern matching
- Custom validators

SQL Injection Prevention:
- SQLAlchemy ORM (no raw SQL)
- Parameterized queries
- Input sanitization
```

---

## 📈 Performance Optimization

### Frontend Optimization

**Streamlit:**
- Session state caching
- Conditional rendering
- Lazy loading of components
- CSS-only animations (no JavaScript)

**Requests:**
- HTTP keep-alive
- Minimal payload size
- JSON compression

### Backend Optimization

**FastAPI:**
- Async request handling
- Connection pooling
- Middleware for caching
- Efficient database queries

**Database:**
- SQLite with proper indexing
- Foreign key constraints
- Efficient schema

**AI/ML:**
- Lightweight embedding model (MiniLM)
- FAISS CPU-only (no GPU needed)
- Chunking strategy optimized for search

### Memory Optimization

**Vector Store:**
- FAISS indexes compressed
- Metadata stored separately
- Per-user vector stores
- Cleanup of old documents

**Conversation Memory:**
- Buffer memory (not full conversation)
- Summarization of old context
- Periodic cleanup

---

## 📊 Scalability Architecture

### Single User (8GB RAM)

- ✅ Streamlit + FastAPI on same machine
- ✅ SQLite database
- ✅ User-specific FAISS index
- ✅ ~1000 documents per user
- ✅ Unlimited conversations

### Multiple Users

**5-10 Users:**
- ✅ Still single machine
- ✅ Multiple FAISS indexes (user-specific)
- ✅ Shared SQLite database
- ✅ Session pooling for API calls

**10-50 Users:**
- ⚠️ May need:
  - Separate backend server
  - Database indexing
  - API rate limiting
  - Memory monitoring

**50+ Users:**
- ❌ Needs upgrade:
  - PostgreSQL (instead of SQLite)
  - Separate frontend/backend
  - Load balancer (Nginx)
  - Redis for caching
  - Distributed FAISS indexes

---

## 🔄 Deployment Architecture

### Single Machine (Default)

```
localhost:8501 ← Streamlit (Frontend)
    ↓
localhost:8000 ← FastAPI (Backend)
    ↓
customer_support.db (SQLite)
vectorstore/ (FAISS)
uploads/ (Documents)
```

### Multi-Machine

```
User Browser
    ↓
nginx:443 (HTTPS, Load Balancer)
    ├─ frontend1.example.com
    ├─ frontend2.example.com
    └─ api.example.com
         ├─ backend1:8000
         ├─ backend2:8000
         └─ backend3:8000
             ↓
         PostgreSQL (Shared DB)
         Redis (Cache)
         S3 (File Storage)
         FAISS (Distributed)
```

---

## 🐳 Container Architecture (Optional Docker)

```
docker-compose.yml
├─ frontend
│  └─ Streamlit container
├─ backend
│  └─ FastAPI container
├─ postgres
│  └─ PostgreSQL container
├─ redis
│  └─ Redis container
└─ nginx
   └─ Reverse proxy
```

---

## 📝 API Architecture

### REST Endpoints

**Authentication:**
```
POST   /api/auth/signup              Create user
POST   /api/auth/login               Get JWT token
POST   /api/auth/change-password     Change password
GET    /api/auth/me                  Get current user
```

**Chat:**
```
POST   /api/chat                     Send message
GET    /api/conversations            List conversations
GET    /api/conversations/{id}       Get conversation
DELETE /api/conversations/{id}       Delete conversation
```

**Documents:**
```
POST   /api/upload                   Upload document
GET    /api/documents                List documents
DELETE /api/documents/{id}           Delete document
```

**Analytics:**
```
GET    /api/analytics                Get user analytics
```

**Admin:**
```
GET    /api/admin/users              List all users
DELETE /api/admin/users/{id}         Delete user
GET    /api/admin/statistics         Platform stats
GET    /api/admin/conversations      All conversations
DELETE /api/admin/conversations/{id} Delete conversation
GET    /api/admin/workflows          Workflow logs
```

---

## 🔗 Integration Points

### External APIs

**OpenAI API:**
- Endpoint: https://api.openai.com/v1/chat/completions
- Model: gpt-3.5-turbo
- Auth: API key in header
- Rate limits: Based on account

### File Processing

**PDF Processing:**
- Library: PyPDF2
- Limitations: Text-based PDFs only
- No OCR for scanned PDFs

**Document Indexing:**
- Library: Sentence Transformers
- Model: all-MiniLM-L6-v2
- Performance: ~1000 docs per minute

---

## 🧪 Testing Architecture

### Unit Tests
```python
# Test Auth
def test_password_hashing()
def test_jwt_token()

# Test RAG
def test_embedding_generation()
def test_faiss_search()

# Test Chat
def test_sentiment_analysis()
def test_query_categorization()
```

### Integration Tests
```python
# Test API endpoints
def test_signup_flow()
def test_chat_flow()
def test_document_upload()

# Test Database
def test_user_creation()
def test_conversation_save()
```

### Load Tests
```bash
# Simulate concurrent users
locust -f locustfile.py --host=http://localhost:8000

# Monitor performance
- Response time
- Memory usage
- CPU usage
```

---

## 🚀 Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] `.env` configured with API keys
- [ ] Database initialized
- [ ] CORS configured
- [ ] Directories created
- [ ] Frontend accessible
- [ ] Backend running
- [ ] Admin account created
- [ ] SSL/TLS certificates (production)
- [ ] Firewall configured
- [ ] Logging enabled
- [ ] Backups scheduled
- [ ] Monitoring in place

---

## 📚 References

- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://sqlalchemy.org
- Streamlit: https://streamlit.io
- LangChain: https://python.langchain.com
- FAISS: https://github.com/facebookresearch/faiss
- Sentence Transformers: https://www.sbert.net

---

This architecture ensures:
- ✅ Scalability from 1 to 1000+ users
- ✅ Security with JWT and bcrypt
- ✅ Performance optimized for low-end devices
- ✅ Maintainability with clean separation of concerns
- ✅ Extensibility for future features
