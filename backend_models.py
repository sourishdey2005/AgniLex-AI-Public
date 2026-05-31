from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./customer_support.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="user")  # user, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="user", cascade="all, delete-orphan")
    workflow_logs = relationship("WorkflowLog", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender = Column(String(20))  # user, assistant
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    filepath = Column(String(500))
    file_type = Column(String(20))  # pdf, txt, docx
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="processing")  # processing, completed, failed

    user = relationship("User", back_populates="documents")


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query_count = Column(Integer, default=0)
    average_latency = Column(Float, default=0.0)
    sentiment = Column(String(50), default="neutral")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analytics")


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    workflow_type = Column(String(100))
    status = Column(String(50))  # success, failed, pending
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workflow_logs")


def init_db():
    """Initialize database and create admin user"""
    Base.metadata.create_all(bind=engine)
    
    # Create admin user if not exists
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            try:
                from backend_auth import get_password_hash
                password_hash = get_password_hash("admin")
            except Exception:
                # Fallback for environments where passlib/bcrypt is misconfigured
                import hashlib
                password_hash = hashlib.sha256("admin".encode("utf-8")).hexdigest()

            admin_user = User(
                username="admin",
                email="admin@localhost.local",
                password_hash=password_hash,
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
