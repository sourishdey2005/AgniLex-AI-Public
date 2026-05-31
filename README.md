# 🤖 AI Customer Support Agent Platform

A complete, production-grade AI Customer Support Agent Platform that runs **fully locally** on low-end devices without Docker, cloud databases, or external dependencies.

## ✨ Features

- **AI Chatbot** - Conversational AI with multi-turn memory and context awareness
- **RAG Pipeline** - Upload documents (PDF, DOCX, TXT) for semantic search
- **Local Vector Database** - FAISS for efficient similarity search
- **Admin Dashboard** - Monitor users, conversations, and analytics
- **User Management** - Authentication with JWT, secure password hashing
- **Analytics** - Track sentiment, query categories, and platform metrics
- **Beautiful UI** - Modern, responsive Streamlit interface with glassmorphism design
- **Lightweight** - Optimized for 8GB RAM systems and basic CPUs

## 🛠 Tech Stack

### Frontend
- **Streamlit** - Interactive web UI
- **Custom CSS** - Modern glassmorphism design
- **Plotly** - Data visualization

### Backend
- **FastAPI** - High-performance API framework
- **SQLite** - Local database (no external DB required)
- **SQLAlchemy** - ORM for database operations

### AI/ML
- **LangChain** - LLM orchestration and memory management
- **OpenAI GPT-3.5** - Language model (requires API key)
- **FAISS** - Vector similarity search
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **PyPDF2** - PDF processing
- **python-docx** - DOCX processing

### Security
- **bcrypt** - Password hashing
- **python-jose** - JWT token generation and verification

---

## 📁 Project Structure

```
customer-support-agent/
│
├── backend_models.py           # SQLAlchemy database models
├── backend_auth.py              # Authentication & JWT logic
├── backend_rag.py               # RAG pipeline with FAISS
├── backend_chat.py              # Chat management & analysis
├── backend_main.py              # FastAPI main application
│
├── frontend_app.py              # Streamlit frontend
│
├── run_backend.py               # Backend runner script
├── run_frontend.py              # Frontend runner script
│
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .env                         # Environment variables (create from .env.example)
│
├── uploads/                     # Uploaded documents storage
├── vectorstore/                 # FAISS vector indexes
├── logs/                        # Application logs
│
├── customer_support.db          # SQLite database (auto-created)
└── README.md                    # This file
```

### File Descriptions

#### Backend Files

**backend_models.py**
- SQLAlchemy ORM models for all database tables
- User, Conversation, Message, Document, Analytics, WorkflowLog
- Auto-creates database on first run
- Creates hardcoded admin account

**backend_auth.py**
- Password hashing with bcrypt
- JWT token creation and verification
- Authentication dependencies for protected routes
- Admin verification logic

**backend_rag.py**
- RAG (Retrieval Augmented Generation) pipeline
- FAISS vector store management
- Document text extraction (PDF, DOCX, TXT)
- Text chunking with sliding windows
- Semantic search with embedding similarity

**backend_chat.py**
- ChatManager class for conversation memory
- Sentiment analysis
- Query categorization
- Escalation detection
- FAQ generation

**backend_main.py**
- FastAPI application with all API routes
- Authentication endpoints (signup, login, password change)
- Chat endpoints (send message, get history, delete conversations)
- File upload and document management
- Analytics API
- Admin controls and monitoring

#### Frontend Files

**frontend_app.py**
- Streamlit main application
- Custom CSS for beautiful UI
- Login and Signup pages
- Chat interface with conversation history
- Document upload interface
- Analytics dashboard
- Settings and password change page
- Admin dashboard with user management

#### Utility Files

**run_backend.py**
- Python script to start FastAPI backend
- Creates directories and initializes database
- Runs on `http://localhost:8000`

**run_frontend.py**
- Python script to start Streamlit frontend
- Checks if backend is running
- Runs on `http://localhost:8501`

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.8+** (Tested on 3.9, 3.10, 3.11)
- **pip** (Python package manager)
- **OpenAI API Key** (Free or Paid account)
- **8GB RAM minimum** (works on 8GB systems)

### Step 1: Clone or Download Project

```bash
cd your-project-directory
```

### Step 2: Create Virtual Environment (Optional but Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI & Uvicorn
- Streamlit
- SQLAlchemy
- LangChain & OpenAI
- FAISS for vector search
- Sentence Transformers
- And more...

### Step 4: Set Up Environment Variables

```bash
# Copy example to .env
cp .env.example .env

# Or on Windows:
copy .env.example .env
```

Edit `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
DATABASE_URL=sqlite:///./customer_support.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
```

### Step 5: Run the Application

#### Terminal 1 - Start Backend

```bash
python run_backend.py
```

You should see:
```
🚀 Starting AI Customer Support Agent Backend...
✅ Created ./uploads directory
✅ Created ./vectorstore directory
✅ Created ./logs directory

🌐 Starting FastAPI Server...
Backend URL: http://localhost:8000
API Docs: http://localhost:8000/docs
```

#### Terminal 2 - Start Frontend

```bash
python run_frontend.py
```

You should see:
```
🚀 Starting AI Customer Support Agent Frontend...
✅ Backend is running on localhost:8000

🌐 Starting Streamlit Frontend...
Frontend URL: http://localhost:8501
```

### Step 6: Access the Application

Open your browser and go to:
```
http://localhost:8501
```

---

## 🔐 Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin`

**⚠️ IMPORTANT:** Change the admin password immediately after first login!

---

## 📝 Usage Guide

### 1. Login / Signup

- Create a new account with username, email, and password (min 8 characters)
- Or login with credentials
- Admin account is pre-created

### 2. Chat Interface

- Start a new conversation
- Ask questions - AI will respond with multi-turn memory
- View conversation history
- Conversations are automatically saved

### 3. Upload Documents

- Go to "Knowledge Base" from sidebar
- Upload PDF, DOCX, or TXT files
- Documents are processed and added to local vector store
- AI uses documents to answer questions with relevant context

### 4. Analytics Dashboard

- View total queries made
- Check average response latency
- See sentiment distribution
- Track active conversations

### 5. Settings

- View account information
- Change password securely
- Logout

### 6. Admin Dashboard (Admin Only)

**Statistics Tab:**
- Total users and active users
- Total conversations and documents
- Message count

**Users Tab:**
- View all user accounts
- Delete users if needed

**Conversations Tab:**
- View all conversations across all users
- Delete any conversation

**Workflows Tab:**
- Monitor all workflow executions
- Check processing logs

---

## 🔑 API Endpoints

### Authentication
```
POST   /api/auth/signup              - Create new user
POST   /api/auth/login               - User login
POST   /api/auth/change-password     - Change password
GET    /api/auth/me                  - Get current user
```

### Chat
```
POST   /api/chat                     - Send message & get response
GET    /api/conversations            - Get all user conversations
GET    /api/conversations/{id}       - Get conversation details
DELETE /api/conversations/{id}       - Delete conversation
```

### Documents
```
POST   /api/upload                   - Upload document
GET    /api/documents                - List user documents
DELETE /api/documents/{id}           - Delete document
```

### Analytics
```
GET    /api/analytics                - Get user analytics
```

### Admin
```
GET    /api/admin/users              - List all users
DELETE /api/admin/users/{id}         - Delete user
GET    /api/admin/statistics         - Platform statistics
GET    /api/admin/conversations      - All conversations
DELETE /api/admin/conversations/{id} - Delete any conversation
GET    /api/admin/workflows          - Workflow logs
```

---

## 🛠 Database Schema

### Users Table
```sql
id (PRIMARY KEY)
username (UNIQUE)
email (UNIQUE)
password_hash
role (user/admin)
is_active
created_at
```

### Conversations Table
```sql
id (PRIMARY KEY)
user_id (FOREIGN KEY)
title
created_at
updated_at
```

### Messages Table
```sql
id (PRIMARY KEY)
conversation_id (FOREIGN KEY)
sender (user/assistant)
content (TEXT)
timestamp
```

### Documents Table
```sql
id (PRIMARY KEY)
user_id (FOREIGN KEY)
filename
filepath
file_type (pdf/txt/docx)
uploaded_at
status (processing/completed/failed)
```

### Analytics Table
```sql
id (PRIMARY KEY)
user_id (FOREIGN KEY)
query_count
average_latency
sentiment (positive/negative/neutral)
created_at
```

### WorkflowLogs Table
```sql
id (PRIMARY KEY)
user_id (FOREIGN KEY)
workflow_type
status (success/failed/pending)
details (TEXT)
timestamp
```

---

## ⚙️ Configuration

### Environment Variables

**OPENAI_API_KEY**
- Your OpenAI API key
- Required for AI responses
- Get from: https://platform.openai.com/api-keys

**SECRET_KEY**
- Used for JWT token signing
- Change in production
- Keep secret

**DATABASE_URL**
- SQLite database location
- Default: `sqlite:///./customer_support.db`
- Stored locally, no external DB needed

**ALGORITHM**
- JWT algorithm (HS256)
- Change only if you know what you're doing

**ACCESS_TOKEN_EXPIRE_MINUTES**
- JWT token validity duration
- Default: 30 minutes

### Performance Tuning

**For Low-End Devices (8GB RAM):**

In `backend_rag.py`, reduce chunk size:
```python
def chunk_text(text: str, chunk_size=256, overlap=50):  # Reduced from 500/100
```

In `backend_chat.py`, reduce search results:
```python
search_results = rag.search(request.message, k=2)  # Reduced from 3
```

**Vector Store Optimization:**

FAISS uses CPU by default (no GPU needed). Vector store files are stored in `./vectorstore/` and compressed automatically.

---

## 🐛 Troubleshooting

### "Connection refused" on localhost:8000

**Problem:** Frontend can't connect to backend

**Solution:**
1. Make sure backend is running: `python run_backend.py`
2. Check if port 8000 is available: `netstat -an | grep 8000`
3. Wait 5 seconds for backend to initialize
4. Restart both processes

### "OPENAI_API_KEY not found"

**Problem:** API calls fail with no API key error

**Solution:**
1. Create `.env` file from `.env.example`
2. Add your actual OpenAI API key
3. Restart backend: `python run_backend.py`

### "Database is locked"

**Problem:** SQLite database is locked

**Solution:**
1. Close all Python processes
2. Delete `customer_support.db`
3. Restart backend - it will recreate the database
4. Note: This deletes all data

### "ModuleNotFoundError"

**Problem:** Module not found when running

**Solution:**
1. Check virtual environment is activated
2. Reinstall requirements: `pip install -r requirements.txt`
3. Make sure you're in the project root directory

### "Port 8000/8501 already in use"

**Problem:** Another application is using the port

**Solution:**

**Find process using port 8000:**
```bash
# On Windows:
netstat -ano | findstr :8000

# On macOS/Linux:
lsof -i :8000
```

Kill the process or use different ports:
```bash
# Backend on different port:
python -m uvicorn backend_main:app --port 8001

# Frontend on different port:
streamlit run frontend_app.py --server.port 8502
```

### "Out of memory" errors

**Problem:** Application uses too much RAM

**Solution:**
1. Reduce vector store size - delete old documents
2. Clear browser cache
3. Reduce number of messages kept in memory
4. Use smaller embedding model

### Slow response time

**Problem:** AI responses are slow

**Solution:**
1. Check internet (OpenAI API calls need network)
2. Check OpenAI API status: https://status.openai.com
3. Reduce context size in RAG
4. Close other applications using CPU

---

## 📊 Monitoring & Logs

### Application Logs

Logs are saved in `./logs/` directory. Check them for errors:

```bash
cat logs/application.log
```

### Database Monitoring

SQLite database file: `customer_support.db`

View with any SQLite viewer or:
```bash
python
>>> import sqlite3
>>> conn = sqlite3.connect('customer_support.db')
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT * FROM users")
>>> print(cursor.fetchall())
```

### API Documentation

FastAPI provides automatic API docs:
```
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

---

## 🔒 Security Best Practices

### For Production Use

1. **Change Admin Password**
   - Edit `backend_models.py` admin user creation
   - Or change password through UI immediately

2. **Change SECRET_KEY**
   - In `.env` file
   - Use strong random string (32+ characters)

3. **Use HTTPS**
   - Deploy behind nginx/reverse proxy with SSL
   - Never expose FastAPI directly to internet

4. **Environment Variables**
   - Never commit `.env` to git
   - Use `.gitignore` to exclude it

5. **Database Backup**
   - Regularly backup `customer_support.db`
   - Store encrypted backups

6. **API Rate Limiting**
   - Add rate limiting middleware
   - Prevent brute force attacks

7. **Input Validation**
   - All inputs are validated with Pydantic
   - SQL injection is prevented by SQLAlchemy ORM

---

## 🚀 Deployment

### Local Network Access

To access from other machines on your network:

**Backend:**
```bash
python -m uvicorn backend_main:app --host 0.0.0.0 --port 8000
# Access from: http://your-ip:8000
```

**Frontend:**
```bash
streamlit run frontend_app.py --server.address 0.0.0.0
# Access from: http://your-ip:8501
```

### Production Deployment

For production use, consider:

1. **Gunicorn** (instead of Uvicorn)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 backend_main:app
   ```

2. **Nginx** (reverse proxy)
   - Handle SSL/TLS
   - Load balancing
   - Static file serving

3. **Systemd** (Linux daemon)
   - Auto-restart on crash
   - Proper logging

4. **Docker** (optional)
   - Create Dockerfile if needed
   - Single container deployment

---

## 📈 Scalability

### Single User (8GB RAM)
- ✅ Perfect performance
- 1000+ conversations possible
- Unlimited documents

### Multiple Users (8GB RAM)
- ✅ Good performance up to 10 concurrent users
- Slight slowdown with 20+ users
- Consider: Reduce vector store, archive old data

### High Traffic (Upgrade Hardware)
- For 100+ concurrent users
- Use PostgreSQL instead of SQLite
- Deploy backend and frontend separately
- Use load balancer (Nginx, HAProxy)
- Add caching layer (Redis)

---

## 🤝 Contributing

To improve this project:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

## 📄 License

This project is provided as-is for educational and commercial use.

---

## ❓ FAQ

**Q: Do I need an OpenAI account?**
A: Yes, you need an OpenAI API key to use the AI features. Create one at https://platform.openai.com

**Q: Will this work offline?**
A: No, the OpenAI API requires internet. Chat history and documents work offline, but AI responses need OpenAI.

**Q: Can I change the embedding model?**
A: Yes, edit `backend_rag.py` line: `EMBEDDING_MODEL = "sentence-transformers/..."`

**Q: How do I backup my data?**
A: Copy `customer_support.db` file. It contains everything except uploaded files.

**Q: Can I use a different LLM?**
A: Yes, edit `backend_chat.py` ChatManager class to use different LLM providers (Hugging Face, Claude, etc.)

**Q: Is there a mobile app?**
A: Not yet. Streamlit responsive design works on mobile browsers.

**Q: Can I deploy to cloud?**
A: Yes, use AWS EC2, DigitalOcean, Heroku, Railway, etc. No Docker needed - just copy files and run.

---

## 📞 Support

For issues:
1. Check troubleshooting section above
2. Check FastAPI logs: http://localhost:8000/docs
3. Check Streamlit logs in terminal
4. Verify `.env` file is correct

---

## 🎉 You're All Set!

Your AI Customer Support Agent is ready to use!

**Access:** http://localhost:8501

**Default Login:**
- Username: `admin`
- Password: `admin`

**Next Steps:**
1. Login with admin account
2. Change admin password in Settings
3. Create user accounts
4. Upload documents to Knowledge Base
5. Start chatting with AI
6. Monitor analytics in dashboard

Happy coding! 🚀
