# 🚀 Deployment & Production Guide

Complete guide for deploying the AI Customer Support Agent to production.

---

## 📋 Pre-Deployment Checklist

### Security
- [ ] Change admin password
- [ ] Change SECRET_KEY in .env
- [ ] Generate strong random SECRET_KEY (32+ chars)
- [ ] Never commit .env to git
- [ ] Add .env to .gitignore
- [ ] SSL/TLS certificates obtained
- [ ] CORS origins configured
- [ ] Input validation enabled
- [ ] Rate limiting configured

### Performance
- [ ] Database backups set up
- [ ] Logging configured
- [ ] Monitoring tools installed
- [ ] Load testing completed
- [ ] Memory usage optimized
- [ ] Database indexes created
- [ ] Cache strategy implemented

### Deployment
- [ ] All dependencies installed
- [ ] Application tested locally
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Firewall rules configured
- [ ] Reverse proxy configured
- [ ] Health checks in place

---

## 🏠 Local Deployment (Default)

### Requirements
- Python 3.8+
- 8GB RAM minimum
- Windows/macOS/Linux

### Setup

```bash
# 1. Clone project
cd customer-support-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 5. Run initialization
python setup.py

# 6. Start backend (Terminal 1)
python run_backend.py

# 7. Start frontend (Terminal 2)
python run_frontend.py

# 8. Access
# Open browser: http://localhost:8501
```

### Database Setup

Database is auto-created on first run:

```
customer_support.db
├── users (with admin account)
├── conversations
├── messages
├── documents
├── analytics
└── workflow_logs
```

---

## ☁️ Cloud Deployment

### Option 1: AWS EC2

#### Instance Setup

```bash
# 1. Launch EC2 instance
# - AMI: Ubuntu 22.04 LTS
# - Instance: t3.medium (1 vCPU, 4GB RAM) or t3.large
# - Storage: 20GB SSD
# - Security Group: Allow 80, 443, 22

# 2. SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# 3. Update system
sudo apt update && sudo apt upgrade -y

# 4. Install Python
sudo apt install python3.10 python3-pip python3-venv -y

# 5. Clone project
git clone https://github.com/your-repo/customer-support-agent.git
cd customer-support-agent

# 6. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 7. Install dependencies
pip install -r requirements.txt

# 8. Configure environment
cp .env.example .env
nano .env  # Edit with OpenAI API key

# 9. Create systemd service for backend
sudo nano /etc/systemd/system/cs-backend.service
```

**Backend Service File:**
```ini
[Unit]
Description=Customer Support AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/customer-support-agent
Environment="PATH=/home/ubuntu/customer-support-agent/venv/bin"
ExecStart=/home/ubuntu/customer-support-agent/venv/bin/python run_backend.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 10. Create systemd service for frontend
sudo nano /etc/systemd/system/cs-frontend.service
```

**Frontend Service File:**
```ini
[Unit]
Description=Customer Support AI Frontend
After=network.target cs-backend.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/customer-support-agent
Environment="PATH=/home/ubuntu/customer-support-agent/venv/bin"
ExecStart=/home/ubuntu/customer-support-agent/venv/bin/python run_frontend.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 11. Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable cs-backend
sudo systemctl enable cs-frontend
sudo systemctl start cs-backend
sudo systemctl start cs-frontend

# 12. Check status
sudo systemctl status cs-backend
sudo systemctl status cs-frontend

# 13. View logs
sudo journalctl -u cs-backend -f
sudo journalctl -u cs-frontend -f
```

#### Nginx Reverse Proxy

```bash
# Install nginx
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/customer-support
```

**Nginx Configuration:**
```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json;
    gzip_min_length 1000;
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streamlit specific
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # API backend
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API documentation
    location /docs {
        proxy_pass http://backend/docs;
    }
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/customer-support /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install SSL certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com
```

---

### Option 2: DigitalOcean

#### Droplet Setup

```bash
# 1. Create Droplet
# - Ubuntu 22.04 x64
# - Basic (1GB RAM) or General Purpose (4GB RAM)
# - Add SSH key

# 2. SSH in
ssh root@your-droplet-ip

# 3. Initial setup
apt update && apt upgrade -y
apt install python3.10 python3-pip python3-venv git nginx -y

# 4. Create app user
useradd -m -s /bin/bash appuser
su - appuser

# 5. Clone project
git clone https://github.com/your-repo/customer-support-agent.git
cd customer-support-agent

# 6. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 7. Install dependencies
pip install -r requirements.txt

# 8. Configure .env
cp .env.example .env
nano .env

# 9. Run setup
python setup.py

# 10. Exit to root
exit

# 11. Create systemd services (same as AWS above)
# ... (follow AWS EC2 systemd service setup)

# 12. Configure Nginx (same as AWS above)
# ... (follow AWS Nginx setup)
```

---

### Option 3: Railway

Railway makes deployment super simple with Git integration.

```bash
# 1. Create account: https://railway.app

# 2. Connect GitHub repo

# 3. Add environment variables
# - OPENAI_API_KEY
# - SECRET_KEY
# - DATABASE_URL (Railway provides PostgreSQL)

# 4. Set start command
# Backend: python run_backend.py
# Frontend: python run_frontend.py

# 5. Deploy
# Automatic on git push
```

---

### Option 4: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run both services
CMD ["sh", "-c", "python run_backend.py & python run_frontend.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://user:password@db:5432/csdb
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads
      - ./vectorstore:/app/vectorstore
      - ./logs:/app/logs

  frontend:
    build: .
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - API_BASE_URL=http://backend:8000/api

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=csdb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🔧 Production Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...

# Security
SECRET_KEY=generate-with-secrets.token_urlsafe(32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./customer_support.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/csdb

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-immediately
```

### Production Improvements

1. **Use PostgreSQL instead of SQLite**
   ```python
   # In backend_models.py
   DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")
   ```

2. **Add Redis caching**
   ```python
   from redis import Redis
   cache = Redis(host='localhost', port=6379, db=0)
   ```

3. **Add Gunicorn for production ASGI**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 backend_main:app
   ```

4. **Enable CORS properly**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST", "DELETE"],
       allow_headers=["*"],
   )
   ```

5. **Add rate limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/api/chat")
   @limiter.limit("30/minute")
   async def chat(...):
       ...
   ```

6. **Add logging**
   ```python
   import logging
   logging.basicConfig(
       filename='logs/app.log',
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend (Streamlit)
curl http://localhost:8501
```

### Database Maintenance

```bash
# Backup database
cp customer_support.db customer_support.db.backup

# Optimize database
sqlite3 customer_support.db "VACUUM;"

# Check size
ls -lh customer_support.db
```

### Log Monitoring

```bash
# View recent errors
tail -100 logs/app.log

# Search for errors
grep ERROR logs/app.log

# Monitor in real-time
tail -f logs/app.log
```

### Resource Monitoring

```bash
# Memory usage
free -h

# CPU usage
top

# Disk usage
df -h

# Process status
ps aux | grep python
```

---

## 🔄 Backup & Recovery

### Automated Backups

Create `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp customer_support.db $BACKUP_DIR/customer_support_$TIMESTAMP.db.gz

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$TIMESTAMP.tar.gz uploads/

# Backup vectorstore
tar -czf $BACKUP_DIR/vectorstore_$TIMESTAMP.tar.gz vectorstore/

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

Schedule with cron:

```bash
# Run backup daily at 2 AM
0 2 * * * /path/to/backup.sh

# Edit crontab
crontab -e
```

### Restore from Backup

```bash
# Restore database
cp backups/customer_support_20240115_020000.db.gz customer_support.db

# Restore uploads
tar -xzf backups/uploads_20240115_020000.tar.gz

# Restore vectorstore
tar -xzf backups/vectorstore_20240115_020000.tar.gz

# Restart services
systemctl restart cs-backend
systemctl restart cs-frontend
```

---

## 🔐 Security Hardening

### SSL/TLS

```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use Let's Encrypt for production
certbot certonly --standalone -d your-domain.com
```

### Firewall Rules

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Environment Security

```bash
# Never log sensitive data
# .env should be in .gitignore
# API keys should be environment variables
# Passwords should be hashed

# Example .gitignore
.env
*.db
*.log
uploads/
vectorstore/
venv/
```

---

## 📈 Performance Tuning

### Database Indexing

```python
# In backend_models.py
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```

### Query Optimization

```python
# Bad: N+1 query problem
conversations = db.query(Conversation).all()
for conv in conversations:
    print(conv.user.username)  # Extra query per conversation

# Good: Eager loading
conversations = db.query(Conversation).join(User).all()
for conv in conversations:
    print(conv.user.username)  # No extra queries
```

### Connection Pooling

```python
# In backend_models.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

---

## 🚨 Troubleshooting Production Issues

### High Memory Usage
- Restart backend service
- Check number of active connections
- Clear old conversations/documents
- Monitor with: `watch -n 1 'free -h'`

### Slow Responses
- Check database indexes
- Monitor API response times
- Check OpenAI API status
- Reduce vector search results (k=2 instead of 3)

### Database Corruption
- Check database integrity: `sqlite3 db.db "PRAGMA integrity_check;"`
- Restore from backup
- Migrate to PostgreSQL

### Service Crashes
- Check logs: `journalctl -u cs-backend -n 50`
- Increase resource limits
- Add memory swap
- Enable auto-restart (already in systemd config)

---

## ✅ Post-Deployment Checklist

- [ ] Admin password changed
- [ ] SSL/TLS working
- [ ] Backups automated
- [ ] Monitoring in place
- [ ] Logging enabled
- [ ] Health checks passing
- [ ] Database optimized
- [ ] Firewall configured
- [ ] Email notifications set up
- [ ] Disaster recovery plan documented

---

Ready for production! 🚀
