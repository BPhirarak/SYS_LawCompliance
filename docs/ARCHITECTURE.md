# System Architecture

## Overview
Thai Law Compliance Management System เป็น full-stack web application ที่ออกแบบมาเพื่อจัดการความสอดคล้องกฎหมายสำหรับโรงงานอุตสาหกรรม ใช้ architecture แบบ monolithic deployment โดย backend (FastAPI) serve frontend static files และ API endpoints

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React SPA (Vite + TailwindCSS)                          │   │
│  │  - Dashboard, LawList, Matrix, Kanban, Help              │   │
│  │  - ChatBot Component (AI Agent UI)                       │   │
│  │  - React Router for navigation                           │   │
│  └────────────────┬─────────────────────────────────────────┘   │
└───────────────────┼─────────────────────────────────────────────┘
                    │ HTTP/HTTPS
                    │ REST API + Static Files
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Server                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  main.py - FastAPI Application                          │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  API Endpoints                                     │  │   │
│  │  │  - /api/laws, /api/departments, /api/tasks        │  │   │
│  │  │  - /api/chat (AI Agent)                           │  │   │
│  │  │  - /api/auth (Authentication)                     │  │   │
│  │  │  - /api/dashboard (Analytics)                     │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                            │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Static File Serving                               │  │   │
│  │  │  - Serves frontend/dist/* at root path            │  │   │
│  │  │  - index.html for SPA routing                     │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────┬───────────────────┬───────────────────┘   │
│                     │                   │                       │
│                     ▼                   ▼                       │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │  database.py             │  │  llm_provider.py         │    │
│  │  - SQLite connection     │  │  - Multi-provider LLM    │    │
│  │  - Schema definition     │  │  - Anthropic Claude      │    │
│  │  - WAL mode              │  │  - OpenAI GPT            │    │
│  └──────────┬───────────────┘  │  - AWS Bedrock           │    │
│             │                  │  - Grok, Ollama          │    │
│             ▼                  │  - OpenRouter            │    │
│  ┌──────────────────────────┐  │  - Tool calling support  │    │
│  │  law.db (SQLite)         │  └──────────┬───────────────┘    │
│  │  - 10 tables             │             │                    │
│  │  - ~17 laws              │             ▼                    │
│  │  - 25 departments        │  ┌──────────────────────────┐    │
│  │  - Tasks, Matrix, etc.   │  │  db_tools.py             │    │
│  └──────────────────────────┘  │  - query_tasks()         │    │
│                                 │  - query_laws()          │    │
│                                 │  - query_departments()   │    │
│                                 │  - query_matrix()        │    │
│                                 │  - query_dashboard()     │    │
│                                 └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                    │
                    │ API Calls
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External LLM Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Anthropic   │  │   OpenAI     │  │ AWS Bedrock  │          │
│  │   Claude     │  │   GPT-4o     │  │   Claude     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Grok       │  │   Ollama     │  │ OpenRouter   │          │
│  │   (xAI)      │  │   (Local)    │  │  (Gateway)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend (React SPA)
```
src/
├── pages/
│   ├── Dashboard.jsx       # Overview + analytics
│   ├── LawList.jsx         # Law browsing + filtering
│   ├── LawMatrix.jsx       # Department-law matrix visualization
│   ├── Kanban.jsx          # Task management board
│   ├── UserManagement.jsx  # Admin user CRUD
│   ├── Help.jsx            # User manual
│   └── Login.jsx           # Authentication
├── components/
│   └── ChatBot.jsx         # AI agent interface
│       ├── ThothIcon       # Custom icon component
│       ├── CopyButton      # Copy message to clipboard
│       ├── LawUpdateCard   # Artifact display
│       ├── MarkdownMessage # Markdown renderer
│       ├── ProviderPanel   # LLM provider selector
│       └── HistoryPanel    # Chat history browser
├── App.jsx                 # Main app + routing + auth
├── main.jsx                # Entry point
└── api.js                  # Axios instance
```

### Backend (FastAPI)
```
backend/
├── main.py                 # FastAPI app + all endpoints
│   ├── Laws endpoints      # CRUD for laws
│   ├── Departments         # Department management
│   ├── Tasks endpoints     # Kanban task CRUD
│   ├── Dashboard           # Analytics aggregation
│   ├── Chat endpoints      # AI agent + tool calling
│   ├── Auth endpoints      # Login + user management
│   └── Static files        # Serve frontend dist/
├── database.py             # SQLite schema + connection
├── llm_provider.py         # Multi-provider LLM abstraction
│   ├── call_llm()          # Simple text generation
│   └── call_llm_with_tools() # Tool calling support
├── db_tools.py             # Tool definitions for AI agent
│   ├── TOOLS               # Anthropic format
│   ├── TOOLS_OPENAI        # OpenAI format
│   └── execute_tool()      # Tool executor
└── seed.py                 # Database initialization
```

## Data Flow

### 1. User Authentication Flow (AD Login)
```
User → Login Page → POST /api/auth/login
                    ↓
                    POST to AD API (http://10.41.97.111:64659/auth/login)
                    ↓
                    AD validates credentials
                    ↓
                    Return AD token + username
                    ↓
                    Sync user to local DB (create if not exists)
                    ↓
                    Generate local token (user_id:random_hex)
                    ↓
                    Return {token, username, role, ad_token}
                    ↓
                    Store in localStorage
                    ↓
                    Redirect to Dashboard

Fallback (if AD_LOGIN_URL not set):
    → Verify credentials from local DB (SHA-256 hash)
    → Generate token
    → Return {token, username, role}
```

### 2. AI Chat Flow (with Tool Calling)
```
User → ChatBot → POST /api/chat
                 ↓
                 Build system prompt + history
                 ↓
                 call_llm_with_tools(system, messages, TOOLS)
                 ↓
                 ┌─────────────────────────────────┐
                 │  Agentic Loop (max 5 rounds)   │
                 │  ┌───────────────────────────┐  │
                 │  │ LLM decides:              │  │
                 │  │ - Answer directly? → text │  │
                 │  │ - Need data? → tool_use   │  │
                 │  └───────────┬───────────────┘  │
                 │              │                  │
                 │              ▼                  │
                 │  ┌───────────────────────────┐  │
                 │  │ If tool_use:              │  │
                 │  │ - execute_tool()          │  │
                 │  │ - Append results          │  │
                 │  │ - Call LLM again          │  │
                 │  └───────────────────────────┘  │
                 └─────────────────────────────────┘
                 ↓
                 Parse <law_update> blocks
                 ↓
                 Auto-apply DB changes (add/update/remove laws)
                 ↓
                 Save session + messages to DB
                 ↓
                 Return {reply, session_id, law_updates}
                 ↓
                 ChatBot renders markdown + artifact cards
```

### 3. Kanban Task Update Flow
```
User → Drag task to new column
       ↓
       PUT /api/tasks/{id} {status: "in_progress"}
       ↓
       UPDATE compliance_tasks SET status=?, updated_at=CURRENT_TIMESTAMP
       ↓
       If status="done" → SET completed_at=NOW()
       ↓
       Return {success: true}
       ↓
       UI updates optimistically
```

## Security Architecture

### Authentication
- **Method**: AD (Active Directory) login + local token
- **AD API**: `http://10.41.97.111:64659/auth/login`
- **Fallback**: Local DB authentication (if AD_LOGIN_URL not set)
- **Token format**: `{user_id}:{random_hex}`
- **Session**: Client-side only (no server-side session)
- **User sync**: AD users auto-created in local DB on first login (role: user)

### Authorization
- **Role-based**: `admin` vs `user`
- **Admin-only endpoints**: User management, system config
- **User endpoints**: All read operations, own password change
- **Protected routes**: React Router checks `auth` state

### API Security
- **CORS**: Allow all origins (development mode)
- **Input validation**: Pydantic models
- **SQL injection**: Parameterized queries
- **XSS**: React auto-escapes, markdown sanitized

## Deployment Architecture

### Single-Server Deployment
```
┌─────────────────────────────────────────┐
│         Production Server               │
│  ┌───────────────────────────────────┐  │
│  │  Uvicorn (ASGI Server)            │  │
│  │  - Port 8000                      │  │
│  │  - Serves FastAPI app             │  │
│  │  - Serves static files (dist/)    │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  SQLite Database (law.db)         │  │
│  │  - WAL mode for concurrency       │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Environment Variables (.env)     │  │
│  │  - API keys (Anthropic, OpenAI)   │  │
│  │  - AWS credentials (Bedrock)      │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Recommended Production Setup
```
Internet
   ↓
Nginx (Reverse Proxy)
   ├── SSL/TLS termination
   ├── Static file caching
   ├── Rate limiting
   └── Proxy to Uvicorn :8000
       ↓
   Uvicorn (FastAPI)
       ├── Application logic
       ├── API endpoints
       └── Static files
           ↓
       SQLite (law.db)
```

## Scalability Considerations

### Current Limitations
- **SQLite**: Single-writer, not suitable for high concurrency
- **Monolithic**: All components in one process
- **No caching**: Every request hits database
- **No queue**: Synchronous processing only

### Future Improvements
1. **Database**: Migrate to PostgreSQL for better concurrency
2. **Caching**: Add Redis for session + query caching
3. **Queue**: Add Celery for async tasks (law scanning, reports)
4. **Microservices**: Split AI agent into separate service
5. **Load balancing**: Multiple backend instances behind Nginx
6. **CDN**: Serve static assets from CDN

## Technology Choices

### Why FastAPI?
- Modern Python async framework
- Auto-generated API docs (Swagger/OpenAPI)
- Pydantic validation
- Easy to deploy (single file possible)
- Good performance for small-medium scale

### Why SQLite?
- Zero configuration
- Single file database
- Good enough for <100 concurrent users
- Easy backup (copy file)
- WAL mode for better concurrency

### Why React + Vite?
- Fast development with HMR
- Modern build tool (faster than Webpack)
- Component-based UI
- Large ecosystem
- Easy to deploy (static files)

### Why Multi-Provider LLM?
- Flexibility: Switch models without code changes
- Cost optimization: Use cheaper models for simple tasks
- Redundancy: Fallback if one provider is down
- Compliance: Use on-premise (Ollama) or AWS (Bedrock) for sensitive data

## Performance Metrics

### Expected Performance
- **API response time**: <100ms (without LLM)
- **LLM response time**: 2-10s (depends on provider/model)
- **Database queries**: <10ms (SQLite with indexes)
- **Frontend load time**: <2s (with caching)
- **Concurrent users**: 10-50 (SQLite limit)

### Bottlenecks
1. **LLM API calls**: Slowest part (2-10s)
2. **SQLite write locks**: Limits concurrent writes
3. **No caching**: Repeated queries hit DB
4. **Single server**: No horizontal scaling

## Monitoring & Logging

### Current Logging
- **FastAPI**: Console logs (uvicorn)
- **Frontend**: Browser console
- **Database**: No query logging

### Recommended Additions
1. **Application logs**: Structured logging (JSON)
2. **Error tracking**: Sentry or similar
3. **Performance monitoring**: APM tool
4. **Database monitoring**: Query performance
5. **LLM usage tracking**: Token usage, costs

## Backup & Recovery

### Database Backup
```bash
# Manual backup
cp law.db law.db.backup

# Automated backup (cron)
0 2 * * * cp /path/to/law.db /backup/law-$(date +\%Y\%m\%d).db
```

### Disaster Recovery
1. **Database**: Restore from backup file
2. **Code**: Pull from Git repository
3. **Environment**: Restore .env file (keep secure backup)
4. **Dependencies**: `pip install -r requirements.txt`

## Development Workflow

### Local Development
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend (optional, for dev)
cd frontend
npm run dev  # Port 5173 with HMR
```

### Production Build
```bash
# Build frontend
cd frontend
npm run build  # Output to dist/

# Start backend (serves frontend)
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Git Workflow
```bash
# Feature branch
git checkout -b feature/new-feature
# ... make changes ...
git add .
git commit -m "feat: description"
git push origin feature/new-feature
# Create PR → Review → Merge to main
```

## API Design Principles

### RESTful Conventions
- `GET /api/resource` — List all
- `GET /api/resource/{id}` — Get one
- `POST /api/resource` — Create
- `PUT /api/resource/{id}` — Update
- `DELETE /api/resource/{id}` — Delete

### Response Format
```json
{
  "data": [...],
  "error": null,
  "meta": {
    "total": 100,
    "page": 1
  }
}
```

### Error Handling
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Future Roadmap

### Phase 1 (Current)
- ✅ Core CRUD operations
- ✅ AI agent with tool calling
- ✅ User management
- ✅ Help documentation

### Phase 2 (Next 3 months)
- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] Email notifications
- [ ] PDF report generation
- [ ] Advanced analytics

### Phase 3 (6-12 months)
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Workflow automation
- [ ] Integration with external systems
- [ ] Multi-language support
