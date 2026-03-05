# Thai Law Compliance Management System

ระบบจัดการความสอดคล้องกฎหมายสำหรับโรงงานอุตสาหกรรมเหล็ก SYS Steel

## 🚀 Quick Start for IT Team

### 1. Clone Repository
```bash
git clone https://github.com/BPhirarak/SYS_LawCompliance.git
cd SYS_LawCompliance
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Create .env file
cp .env.example .env  # (if exists)
nano .env

# Add configuration:
# Active Directory Login
AD_LOGIN_URL=http://10.41.97.111:64659/auth/login

# LLM Provider
LLM_PROVIDER=bedrock
AWS_BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### 4. Initialize Database
```bash
python seed.py
```

### 5. Run Application
```bash
# Development
python -m uvicorn main:app --reload --port 8000

# Production
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Access Application
- **App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Login**: Use your AD (Active Directory) credentials
- **Fallback Login** (if AD not configured): `admin1` / `adm1219`

---

## 📚 Documentation

### For IT Team
- **[Deployment Guide](docs/DEPLOYMENT.md)** — Complete deployment instructions
- **[Architecture](docs/ARCHITECTURE.md)** — System architecture & design
- **[Database Schema](docs/DATABASE.md)** — ERD & table definitions

### For Users
- **[User Manual](docs/README.md)** — Features & API reference
- **Help Page** — In-app help at `/help`

---

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: SQLite with WAL mode
- **Frontend**: React 18 + Vite + TailwindCSS
- **AI/LLM**: Multi-provider (Anthropic, OpenAI, AWS Bedrock, Grok, Ollama, OpenRouter)

---

## 📦 Project Structure

```
SYS_LawCompliance/
├── backend/              # FastAPI application
│   ├── main.py          # API endpoints
│   ├── database.py      # SQLite schema
│   ├── llm_provider.py  # Multi-provider LLM
│   ├── db_tools.py      # Tool calling for AI
│   ├── requirements.txt # Python dependencies
│   └── .env            # Environment variables (DO NOT COMMIT)
├── frontend/            # React application
│   ├── src/            # Source code
│   └── dist/           # Built static files (served by backend)
├── docs/               # Documentation
│   ├── README.md       # User manual
│   ├── DEPLOYMENT.md   # Deployment guide
│   ├── ARCHITECTURE.md # System architecture
│   └── DATABASE.md     # Database schema
└── start.bat           # Windows startup script
```

---

## 🔐 Security Notes

### ⚠️ IMPORTANT
1. **AD Login configured** — Uses company AD credentials
2. **Never commit `.env` file** — Contains sensitive API keys
3. **Admin role assignment** — Auto-assigned to: banpotp@syssteel.com, piyawats@syssteel.com, thirayur@syssteel.com (configurable in .env)
4. **Use HTTPS in production** — Setup SSL certificate
5. **Restrict database access** — `chmod 600 law.db`
6. **Rotate API keys regularly** — Every 90 days recommended

---

## 🚢 Deployment Options

### Option 1: Systemd Service (Linux - Recommended)
```bash
# See docs/DEPLOYMENT.md for complete guide
sudo systemctl enable lawcompliance
sudo systemctl start lawcompliance
```

### Option 2: Docker
```bash
docker-compose up -d
```

### Option 3: Windows Service
```bash
# Using NSSM (see docs/DEPLOYMENT.md)
nssm install LawCompliance
```

### Option 4: Nginx Reverse Proxy (Production)
```bash
# See docs/DEPLOYMENT.md for Nginx configuration
sudo systemctl restart nginx
```

---

## 🔧 Configuration

### Environment Variables (.env)

**Required:**
```bash
# Active Directory Login (recommended)
AD_LOGIN_URL=http://10.41.97.111:64659/auth/login
# Comment out to use local DB authentication

# LLM Provider
LLM_PROVIDER=bedrock  # or anthropic, openai, grok, ollama, openrouter
```

**AWS Bedrock (Recommended):**
```bash
AWS_BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

**Anthropic Claude (Alternative):**
```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-opus-4-5
```

**OpenAI (Alternative):**
```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
```

---

## 🎯 Features

### Core Features
- ✅ Dashboard with compliance overview
- ✅ Law management (17+ laws, 9 categories)
- ✅ Department-law matrix (25 departments)
- ✅ Compliance Kanban board
- ✅ AI chatbot with tool calling (Thoth-Legal Agent)
- ✅ User management (role-based access)
- ✅ Help documentation

### AI Agent Capabilities
- Natural language Q&A about laws
- Query database directly (tool calling)
- Multi-provider LLM support
- Chat history & session management
- Stop generation mid-process
- Markdown rendering with tables

---

## 📊 System Requirements

### Minimum
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB
- **OS**: Linux (Ubuntu 20.04+) or Windows Server 2019+

### Recommended
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 20GB
- **OS**: Ubuntu 22.04 LTS

---

## 🔄 Maintenance

### Update Application
```bash
git pull origin main
cd backend
pip install -r requirements.txt --upgrade
sudo systemctl restart lawcompliance
```

### Backup Database
```bash
cp backend/law.db backup/law-$(date +%Y%m%d).db
```

### View Logs
```bash
sudo journalctl -u lawcompliance -f
```

---

## 🐛 Troubleshooting

### Common Issues

**Port 8000 already in use:**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

**Permission denied on law.db:**
```bash
sudo chown www-data:www-data backend/law.db
sudo chmod 664 backend/law.db
```

**LLM API errors:**
- Check .env file has correct API keys
- Verify API key permissions
- Check network connectivity

**Frontend not loading:**
- Verify `frontend/dist/` exists
- Check Nginx configuration
- Clear browser cache

---

## 📞 Support

### Documentation
- **Deployment Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Database Schema**: [docs/DATABASE.md](docs/DATABASE.md)
- **API Docs**: http://your-server:8000/docs

### Contact
- **GitHub**: https://github.com/BPhirarak/SYS_LawCompliance
- **Issues**: https://github.com/BPhirarak/SYS_LawCompliance/issues

---

## 📝 License

Proprietary - SYS Steel Internal Use Only

---

## 🎉 Credits

Developed for SYS Steel by [Your Name/Team]

**Version**: 1.0.0  
**Last Updated**: 2026-03-05
