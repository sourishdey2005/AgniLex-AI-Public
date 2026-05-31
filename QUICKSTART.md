# ⚡ Quick Start Guide

Get your AI Customer Support Agent running in **5 minutes**.

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.8+ installed
- ✅ OpenAI API key (from https://platform.openai.com)
- ✅ At least 8GB RAM
- ✅ Internet connection

---

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)

```bash
pip install -r requirements.txt
```

Expected output: All packages installed successfully ✅

### Step 2: Configure Environment (1 min)

Copy and edit `.env`:

```bash
# Copy example
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

**Don't have an OpenAI key?**
1. Go to https://platform.openai.com/account/api-keys
2. Create new API key
3. Paste it in `.env`

### Step 3: Start Backend (30 sec)

Open Terminal 1:

```bash
python run_backend.py
```

Wait for message: `✅ FastAPI Server running on http://localhost:8000`

### Step 4: Start Frontend (30 sec)

Open Terminal 2:

```bash
python run_frontend.py
```

Wait for message: `✅ Frontend running on http://localhost:8501`

### Step 5: Login (1 min)

Open browser: http://localhost:8501

Login with:
- **Username:** admin
- **Password:** admin

**Change your password immediately!** Go to Settings ⚙️ → Change Password

---

## First Steps in the App

### 1. Chat with AI

1. Click "💬 Chat with AI Agent"
2. Type a question
3. AI responds instantly

### 2. Upload Documents

1. Click "📄 Knowledge Base" in sidebar
2. Upload a PDF, DOCX, or TXT file
3. AI will use it to answer questions

### 3. View Analytics

1. Click "📊 Analytics" in sidebar
2. See queries, conversations, sentiment

### 4. Create User Account

1. Logout (click logout button)
2. Click "Don't have account? Sign up"
3. Create new account

---

## Common Commands

### Stop Backend
Press `Ctrl+C` in Backend terminal

### Stop Frontend
Press `Ctrl+C` in Frontend terminal

### Reset Database
```bash
rm customer_support.db
python run_backend.py
```

### View API Documentation
Open: http://localhost:8000/docs

---

## Troubleshooting Quick Fixes

**"Connection refused"**
- Make sure backend is running in Terminal 1
- Wait 5 seconds and refresh browser

**"OPENAI_API_KEY not found"**
- Check `.env` file has your API key
- Restart backend: `Ctrl+C` then `python run_backend.py`

**"Port 8000 already in use"**
- Another app is using port 8000
- Change port in `run_backend.py` if needed

**"Slow responses"**
- Check your internet connection
- OpenAI API might be slow

---

## Next Steps

After setup works:

1. **Explore Admin Dashboard** (login as admin)
   - View all users
   - Monitor conversations
   - Check statistics

2. **Upload Documents**
   - PDFs, DOCX, TXT files
   - AI searches them for answers

3. **Change Admin Password**
   - Security first!
   - Settings ⚙️ → Change Password

4. **Create Test Users**
   - Sign up with different accounts
   - Test multi-user functionality

5. **Monitor Logs**
   - Check `./logs/` folder
   - See API calls and errors

---

## 🎯 You're Ready!

Your AI Customer Support Agent is running.

**Access:** http://localhost:8501

Enjoy! 🚀

---

## Need Help?

1. Check README.md for detailed guide
2. Check API docs at http://localhost:8000/docs
3. Check logs in `./logs/` folder
4. Restart both backend and frontend

**Still stuck?** Check the Troubleshooting section in README.md
