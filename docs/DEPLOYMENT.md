# Deployment Guide

## สำหรับ IT Team

คู่มือนี้อธิบายขั้นตอนการ deploy Thai Law Compliance Management System ขึ้น production server

## Prerequisites

### Server Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended) หรือ Windows Server 2019+
- **CPU**: 2 cores minimum (4 cores recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 10GB minimum
- **Network**: Internet access สำหรับ LLM API calls

### Software Requirements
- **Python**: 3.10 or higher
- **pip**: Python package manager
- **Git**: For cloning repository

### Optional (Recommended for Production)
- **Nginx**: Reverse proxy + SSL termination
- **Systemd**: Service management (Linux)
- **Certbot**: SSL certificate (Let's Encrypt)

---

## Quick Deployment (Single Server)

### Step 1: Clone Repository
```bash
# SSH to production server
ssh user@your-server.com

# Clone repository
git clone https://github.com/BPhirarak/SYS_LawCompliance.git
cd SYS_LawCompliance
```

### Step 2: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
```bash
# Copy example .env (if exists) or create new
nano .env
```

**Required .env configuration:**
```bash
# LLM Provider (choose one: anthropic | openai | bedrock | grok | ollama | openrouter)
LLM_PROVIDER=bedrock

# Active Directory Login (recommended for production)
AD_LOGIN_URL=http://10.41.97.111:64659/auth/login
# Comment out above line to use local DB authentication

# Admin Users (comma-separated email list)
ADMIN_USERS=banpotp@syssteel.com,piyawats@syssteel.com,thirayur@syssteel.com

# AWS Bedrock (recommended for production)
AWS_BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# OR Anthropic Claude (alternative)
# ANTHROPIC_API_KEY=sk-ant-...
# ANTHROPIC_MODEL=claude-opus-4-5

# OR OpenAI (alternative)
# OPENAI_API_KEY=sk-proj-...
# OPENAI_MODEL=gpt-4o
```

**⚠️ SECURITY WARNING:**
- ไม่ควร commit `.env` file ขึ้น Git
- ใช้ environment variables หรือ secrets management
- Rotate API keys เป็นประจำ

### Step 4: Initialize Database
```bash
python seed.py
```

This will create `law.db` with:
- 9 law categories
- 17+ laws
- 25 departments
- Department-law matrix
- Sample compliance tasks
- Default admin user (admin1 / adm1219)

### Step 5: Test Run
```bash
# Test run (development mode)
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Access: http://your-server-ip:8000
# API Docs: http://your-server-ip:8000/docs
```

### Step 6: Production Run with Systemd (Linux)

Create systemd service file:
```bash
sudo nano /etc/systemd/system/lawcompliance.service
```

**Service file content:**
```ini
[Unit]
Description=Thai Law Compliance Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/SYS_LawCompliance/backend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable lawcompliance
sudo systemctl start lawcompliance
sudo systemctl status lawcompliance
```

**View logs:**
```bash
sudo journalctl -u lawcompliance -f
```

---

## Production Deployment with Nginx (Recommended)

### Step 1: Install Nginx
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### Step 2: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/lawcompliance
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    client_max_body_size 10M;

    # Frontend static files
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for LLM API calls
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/lawcompliance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 3: Setup SSL with Let's Encrypt (Optional but Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

---

## Windows Server Deployment

### Option 1: Run as Windows Service (using NSSM)

**Install NSSM:**
```powershell
# Download from https://nssm.cc/download
# Extract to C:\nssm

# Install service
C:\nssm\nssm.exe install LawCompliance "C:\Python310\python.exe" "-m uvicorn main:app --host 0.0.0.0 --port 8000"
C:\nssm\nssm.exe set LawCompliance AppDirectory "C:\path\to\SYS_LawCompliance\backend"
C:\nssm\nssm.exe start LawCompliance
```

### Option 2: Run with IIS + FastCGI

1. Install IIS with CGI support
2. Install Python 3.10+
3. Configure FastCGI module
4. Create web.config (see below)

**web.config:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="Python FastCGI" path="*" verb="*" modules="FastCgiModule" 
           scriptProcessor="C:\Python310\python.exe|C:\Python310\Lib\site-packages\wfastcgi.py" 
           resourceType="Unspecified" requireAccess="Script" />
    </handlers>
  </system.webServer>
</configuration>
```

---

## Docker Deployment (Alternative)

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .
COPY frontend/dist/ ./dist/

# Initialize database
RUN python seed.py

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  lawcompliance:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=bedrock
      - AWS_BEDROCK_REGION=us-east-1
      - BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

**Deploy:**
```bash
docker-compose up -d
```

---

## Post-Deployment Checklist

### 1. Security
- [ ] Setup AD login URL in .env
- [ ] Configure ADMIN_USERS list in .env
- [ ] Change default admin password (admin1 / adm1219) — for local fallback only
- [ ] Setup SSL/TLS certificate
- [ ] Configure firewall (allow only 80/443)
- [ ] Restrict .env file permissions (`chmod 600 .env`)
- [ ] Enable fail2ban or similar
- [ ] Setup backup for law.db
- [ ] Verify AD users auto-sync with correct roles

### 2. Monitoring
- [ ] Setup application logs
- [ ] Configure error tracking (Sentry)
- [ ] Monitor disk space
- [ ] Monitor API usage/costs
- [ ] Setup uptime monitoring

### 3. Backup
- [ ] Automated database backup (daily)
- [ ] Backup .env file (secure location)
- [ ] Test restore procedure

### 4. Testing
- [ ] Test login with default credentials
- [ ] Test all menu pages (Dashboard, Laws, Matrix, Kanban)
- [ ] Test AI chatbot with sample questions
- [ ] Test user management (create/delete users)
- [ ] Test on different browsers

---

## Maintenance

### Update Application
```bash
cd SYS_LawCompliance
git pull origin main
cd backend
pip install -r requirements.txt --upgrade
sudo systemctl restart lawcompliance
```

### Database Backup
```bash
# Manual backup
cp backend/law.db backup/law-$(date +%Y%m%d).db

# Automated backup (cron)
0 2 * * * cp /path/to/law.db /backup/law-$(date +\%Y\%m\%d).db
```

### View Logs
```bash
# Systemd service logs
sudo journalctl -u lawcompliance -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Service
```bash
sudo systemctl restart lawcompliance
sudo systemctl restart nginx
```

---

## Troubleshooting

### Issue: Port 8000 already in use
```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill process
sudo kill -9 <PID>
```

### Issue: Permission denied on law.db
```bash
sudo chown www-data:www-data backend/law.db
sudo chmod 664 backend/law.db
```

### Issue: LLM API errors
- Check .env file has correct API keys
- Verify API key permissions
- Check network connectivity
- Review API usage limits/quotas

### Issue: Frontend not loading
- Verify `frontend/dist/` exists
- Check Nginx configuration
- Clear browser cache
- Check browser console for errors

---

## Performance Tuning

### Uvicorn Workers
```bash
# Increase workers for better concurrency
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Database Optimization
```sql
-- Analyze database
ANALYZE;

-- Vacuum database
VACUUM;
```

### Nginx Caching
```nginx
# Add to nginx config
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Support

### Documentation
- **User Manual**: http://your-domain.com/help
- **API Docs**: http://your-domain.com/docs
- **Technical Docs**: `/docs/` folder in repository

### Contact
- **IT Support**: [your-it-email@syssteel.com]
- **Developer**: [developer-email@syssteel.com]
- **GitHub Issues**: https://github.com/BPhirarak/SYS_LawCompliance/issues

---

## License
Proprietary - SYS Steel Internal Use Only
