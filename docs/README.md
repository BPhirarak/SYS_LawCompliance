# Thai Law Compliance Management System

## Overview
ระบบจัดการความสอดคล้องกฎหมายสำหรับโรงงานอุตสาหกรรมเหล็ก SYS Steel ช่วยติดตามและจัดการกฎหมายที่เกี่ยวข้องกับการดำเนินงาน ครอบคลุม 9 หมวดหมู่กฎหมาย และ 25 หน่วยงานภายในองค์กร

## Tech Stack
- **Backend**: FastAPI (Python 3.10+)
- **Database**: SQLite with WAL mode
- **Frontend**: React 18 + Vite + TailwindCSS
- **AI/LLM**: Multi-provider support (Anthropic Claude, OpenAI, AWS Bedrock, Grok, Ollama, OpenRouter)
- **Deployment**: Single-server deployment (backend serves frontend static files)

## Project Structure
```
-5-ThaiLawCompliance/
├── backend/
│   ├── main.py              # FastAPI app + API endpoints
│   ├── database.py          # SQLite schema + connection
│   ├── llm_provider.py      # Multi-provider LLM abstraction
│   ├── db_tools.py          # Tool calling functions for AI agent
│   ├── seed.py              # Database seeding script
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (API keys, config)
│   └── law.db               # SQLite database file
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages (Dashboard, LawList, Matrix, Kanban, Help, etc.)
│   │   ├── components/      # React components (ChatBot)
│   │   ├── App.jsx          # Main app component + routing
│   │   └── main.jsx         # Entry point
│   ├── dist/                # Built static files (served by backend)
│   ├── package.json
│   └── vite.config.js
├── docs/                    # Documentation
│   ├── README.md            # This file
│   ├── ARCHITECTURE.md      # System architecture
│   ├── DATABASE.md          # Database schema + ERD
│   └── DEPLOYMENT.md        # Deployment guide
└── start.bat                # Windows startup script
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend development only)
- Git

### Installation
1. Clone repository:
```bash
git clone https://github.com/BPhirarak/SYS_LawCompliance.git
cd SYS_LawCompliance
```

2. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. Initialize database:
```bash
python seed.py
```

5. Start the system:
```bash
# Windows
..\start.bat

# Linux/Mac
uvicorn main:app --reload --port 8000
```

6. Access the application:
- App: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Default Credentials
- Username: `admin1`
- Password: `adm1219`

## Features

### 1. Dashboard
- Overview of compliance status
- Task summary by status and priority
- Charts showing distribution by department and law category
- Recent law updates

### 2. Law Management
- Browse all laws with filtering by category and risk level
- View law details, penalties, and related departments
- Direct links to official government sources

### 3. Law Matrix
- Visual matrix showing department ↔ law relationships
- Filter by law category
- Hover tooltips with law details
- Color-coded relevance levels (Primary/High/Medium)

### 4. Compliance Kanban
- Drag-and-drop task management (Todo → In Progress → Done)
- Filter by department, law, and priority
- Edit task details, assignee, and due dates
- Priority levels: Critical, High, Medium, Low

### 5. Thoth-Legal Agent (AI Chatbot)
- Natural language Q&A about laws and compliance
- Tool calling — agent can query database directly
- Multi-provider LLM support (switch models on-the-fly)
- Chat history and session management
- Stop generation mid-process
- Markdown rendering with tables, code blocks, lists

### 6. User Management (Admin only)
- Add/remove user accounts
- Role-based access control (admin/user)
- Password reset functionality
- Self-service password change

## API Endpoints

### Laws
- `GET /api/laws` — List all laws
- `GET /api/laws/{id}` — Get law details
- `PUT /api/laws/{id}` — Update law
- `POST /api/laws/{id}/updates` — Add law update record

### Departments
- `GET /api/departments` — List all departments
- `GET /api/departments/meta/matrix` — Get department-law matrix
- `PUT /api/departments/meta/matrix` — Update matrix relationship

### Tasks
- `GET /api/tasks` — List tasks (with filters)
- `POST /api/tasks` — Create task
- `PUT /api/tasks/{id}` — Update task
- `DELETE /api/tasks/{id}` — Delete task

### Chat Agent
- `POST /api/chat` — Send message to AI agent
- `GET /api/chat/provider` — Get current LLM provider/model
- `POST /api/chat/provider` — Change LLM provider/model
- `GET /api/chat/sessions` — Get chat history
- `GET /api/chat/sessions/{id}` — Load specific session
- `DELETE /api/chat/sessions/{id}` — Delete session

### Auth
- `POST /api/auth/login` — User login
- `GET /api/auth/users` — List users (admin only)
- `POST /api/auth/users` — Create user (admin only)
- `DELETE /api/auth/users/{id}` — Delete user (admin only)
- `POST /api/auth/users/{id}/reset-password` — Reset password (admin only)
- `POST /api/auth/change-password` — Change own password

## Configuration

### Environment Variables (.env)
```bash
# LLM Provider (anthropic | openai | bedrock | grok | ollama | openrouter)
LLM_PROVIDER=bedrock

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-opus-4-5

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o

# AWS Bedrock
AWS_BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Grok (xAI)
GROK_API_KEY=xai-...
GROK_MODEL=grok-3-mini

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# OpenRouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

## Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev  # Dev server on port 5173
npm run build  # Build for production
```

### Backend Development
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Database Migrations
Database schema is defined in `backend/database.py`. To reset database:
```bash
rm law.db
python seed.py
```

## Testing
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment guide.

## License
Proprietary - SYS Steel Internal Use Only

## Support
For technical support, contact IT Department or refer to the Help page in the application.
