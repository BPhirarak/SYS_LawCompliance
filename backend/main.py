from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from database import get_conn, init_db
import os, uuid, datetime, json, asyncio

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

app = FastAPI(title="Thai Law Compliance API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_db()

def rows(cursor): return [dict(r) for r in cursor.fetchall()]
def row(cursor): r = cursor.fetchone(); return dict(r) if r else None

# ── LAWS ──────────────────────────────────────────────────────────────────────
@app.get("/api/laws")
def get_laws(category: str = None, risk_level: str = None, search: str = None):
    conn = get_conn()
    q = "SELECT l.*, lc.name_th as category_name, lc.code as category_code FROM laws l LEFT JOIN law_categories lc ON l.category_id=lc.id WHERE 1=1"
    p = []
    if category: q += " AND lc.code=?"; p.append(category)
    if risk_level: q += " AND l.risk_level=?"; p.append(risk_level)
    if search: q += " AND (l.name_th LIKE ? OR l.description LIKE ?)"; p += [f"%{search}%", f"%{search}%"]
    q += " ORDER BY CASE l.risk_level WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, l.code"
    result = rows(conn.execute(q, p))
    conn.close(); return result

@app.get("/api/laws/meta/categories")
def get_categories():
    conn = get_conn()
    result = rows(conn.execute("SELECT * FROM law_categories ORDER BY code"))
    conn.close(); return result

@app.get("/api/laws/{law_id}")
def get_law(law_id: int):
    conn = get_conn()
    law = row(conn.execute("SELECT l.*, lc.name_th as category_name FROM laws l LEFT JOIN law_categories lc ON l.category_id=lc.id WHERE l.id=?", (law_id,)))
    if not law: raise HTTPException(404)
    law["departments"] = rows(conn.execute("SELECT d.*, dlm.relevance_level FROM departments d JOIN department_law_matrix dlm ON d.id=dlm.department_id WHERE dlm.law_id=?", (law_id,)))
    law["updates"] = rows(conn.execute("SELECT * FROM law_updates WHERE law_id=? ORDER BY detected_at DESC LIMIT 10", (law_id,)))
    conn.close(); return law

class LawUpdate(BaseModel):
    name_th: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    penalty_summary: Optional[str] = None
    source_url: Optional[str] = None

@app.put("/api/laws/{law_id}")
def update_law(law_id: int, body: LawUpdate):
    conn = get_conn()
    conn.execute("UPDATE laws SET name_th=COALESCE(?,name_th), description=COALESCE(?,description), risk_level=COALESCE(?,risk_level), status=COALESCE(?,status), penalty_summary=COALESCE(?,penalty_summary), source_url=COALESCE(?,source_url), updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (body.name_th, body.description, body.risk_level, body.status, body.penalty_summary, body.source_url, law_id))
    conn.commit(); conn.close(); return {"success": True}

class LawUpdateRecord(BaseModel):
    update_type: str
    summary: str
    source: Optional[str] = None

@app.post("/api/laws/{law_id}/updates")
def add_law_update(law_id: int, body: LawUpdateRecord):
    conn = get_conn()
    r = conn.execute("INSERT INTO law_updates (law_id, update_type, summary, source) VALUES (?,?,?,?)", (law_id, body.update_type, body.summary, body.source))
    conn.commit(); lid = r.lastrowid; conn.close(); return {"id": lid}

# ── DEPARTMENTS ───────────────────────────────────────────────────────────────
@app.get("/api/departments")
def get_departments():
    conn = get_conn()
    result = rows(conn.execute("SELECT * FROM departments ORDER BY code"))
    conn.close(); return result

@app.get("/api/departments/meta/matrix")
def get_matrix():
    conn = get_conn()
    departments = rows(conn.execute("SELECT * FROM departments ORDER BY code"))
    laws_list = rows(conn.execute("SELECT l.*, lc.code as category_code, lc.name_th as category_name FROM laws l JOIN law_categories lc ON l.category_id=lc.id ORDER BY lc.code, l.code"))
    matrix_rows = rows(conn.execute("SELECT * FROM department_law_matrix"))
    matrix_map = {}
    for m in matrix_rows:
        matrix_map.setdefault(str(m["department_id"]), {})[str(m["law_id"])] = m["relevance_level"]
    conn.close()
    return {"departments": departments, "laws": laws_list, "matrix": matrix_map}

class MatrixUpdate(BaseModel):
    department_id: int
    law_id: int
    relevance_level: str

@app.put("/api/departments/meta/matrix")
def update_matrix(body: MatrixUpdate):
    conn = get_conn()
    conn.execute("INSERT INTO department_law_matrix (department_id, law_id, relevance_level) VALUES (?,?,?) ON CONFLICT(department_id, law_id) DO UPDATE SET relevance_level=excluded.relevance_level",
        (body.department_id, body.law_id, body.relevance_level))
    conn.commit(); conn.close(); return {"success": True}

@app.get("/api/departments/{dept_id}/laws")
def get_dept_laws(dept_id: int):
    conn = get_conn()
    result = rows(conn.execute("SELECT l.*, lc.name_th as category_name, dlm.relevance_level FROM laws l JOIN department_law_matrix dlm ON l.id=dlm.law_id JOIN law_categories lc ON l.category_id=lc.id WHERE dlm.department_id=? ORDER BY dlm.relevance_level DESC, l.risk_level DESC", (dept_id,)))
    conn.close(); return result

# ── TASKS ─────────────────────────────────────────────────────────────────────
@app.get("/api/tasks")
def get_tasks(department_id: int = None, law_id: int = None, status: str = None):
    conn = get_conn()
    q = "SELECT ct.*, l.name_th as law_name, l.code as law_code, l.risk_level, d.name_th as dept_name, d.code as dept_code FROM compliance_tasks ct LEFT JOIN laws l ON ct.law_id=l.id LEFT JOIN departments d ON ct.department_id=d.id WHERE 1=1"
    p = []
    if department_id: q += " AND ct.department_id=?"; p.append(department_id)
    if law_id: q += " AND ct.law_id=?"; p.append(law_id)
    if status: q += " AND ct.status=?"; p.append(status)
    q += " ORDER BY CASE ct.priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, ct.created_at DESC"
    result = rows(conn.execute(q, p))
    conn.close(); return result

class TaskCreate(BaseModel):
    law_id: int
    department_id: int
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assignee: Optional[str] = None
    plan: Optional[str] = None
    due_date: Optional[str] = None

@app.post("/api/tasks")
def create_task(body: TaskCreate):
    conn = get_conn()
    r = conn.execute("INSERT INTO compliance_tasks (law_id, department_id, title, description, priority, assignee, plan, due_date) VALUES (?,?,?,?,?,?,?,?)",
        (body.law_id, body.department_id, body.title, body.description, body.priority, body.assignee, body.plan, body.due_date))
    conn.commit(); tid = r.lastrowid; conn.close(); return {"id": tid}

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assignee: Optional[str] = None
    plan: Optional[str] = None
    due_date: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    conn = get_conn()
    completed_at = datetime.datetime.now().isoformat() if body.status == "done" else None
    conn.execute("UPDATE compliance_tasks SET status=COALESCE(?,status), assignee=COALESCE(?,assignee), plan=COALESCE(?,plan), due_date=COALESCE(?,due_date), title=COALESCE(?,title), description=COALESCE(?,description), priority=COALESCE(?,priority), completed_at=COALESCE(?,completed_at), updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (body.status, body.assignee, body.plan, body.due_date, body.title, body.description, body.priority, completed_at, task_id))
    conn.commit(); conn.close(); return {"success": True}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM compliance_tasks WHERE id=?", (task_id,))
    conn.commit(); conn.close(); return {"success": True}

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
@app.get("/api/dashboard")
def get_dashboard(department_id: int = None):
    conn = get_conn()
    p = (department_id,) if department_id else ()
    dept_filter = "WHERE ct.department_id=?" if department_id else ""
    summary = row(conn.execute(f"SELECT COUNT(*) as total, SUM(CASE WHEN status='todo' THEN 1 ELSE 0 END) as todo, SUM(CASE WHEN status='doing' THEN 1 ELSE 0 END) as doing, SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) as done, SUM(CASE WHEN priority='critical' AND status!='done' THEN 1 ELSE 0 END) as critical_open, SUM(CASE WHEN due_date < date('now') AND status!='done' THEN 1 ELSE 0 END) as overdue FROM compliance_tasks ct {dept_filter}", p))
    by_dept = rows(conn.execute("SELECT d.code, d.name_th, SUM(CASE WHEN ct.status='todo' THEN 1 ELSE 0 END) as todo, SUM(CASE WHEN ct.status='doing' THEN 1 ELSE 0 END) as doing, SUM(CASE WHEN ct.status='done' THEN 1 ELSE 0 END) as done, COUNT(ct.id) as total FROM departments d LEFT JOIN compliance_tasks ct ON d.id=ct.department_id GROUP BY d.id ORDER BY d.code"))
    by_category = rows(conn.execute("SELECT lc.name_th as category, lc.code, SUM(CASE WHEN ct.status='todo' THEN 1 ELSE 0 END) as todo, SUM(CASE WHEN ct.status='doing' THEN 1 ELSE 0 END) as doing, SUM(CASE WHEN ct.status='done' THEN 1 ELSE 0 END) as done FROM law_categories lc LEFT JOIN laws l ON lc.id=l.category_id LEFT JOIN compliance_tasks ct ON l.id=ct.law_id GROUP BY lc.id ORDER BY lc.code"))
    recent_updates = rows(conn.execute("SELECT lu.*, l.name_th as law_name FROM law_updates lu JOIN laws l ON lu.law_id=l.id ORDER BY lu.detected_at DESC LIMIT 5"))
    law_stats = rows(conn.execute("SELECT risk_level, COUNT(*) as count FROM laws GROUP BY risk_level"))
    conn.close()
    return {"summary": summary, "byDept": by_dept, "byCategory": by_category, "recentUpdates": recent_updates, "lawStats": law_stats}

# ── CHAT AGENT ────────────────────────────────────────────────────────────────
from llm_provider import call_llm, call_llm_with_tools, get_provider
from db_tools import TOOLS, TOOLS_OPENAI, execute_tool

def get_laws_context():
    conn = get_conn()
    laws = [dict(r) for r in conn.execute(
        "SELECT l.code, l.name_th, l.description, l.risk_level, l.penalty_summary, l.effective_date, lc.name_th as category FROM laws l JOIN law_categories lc ON l.category_id=lc.id ORDER BY l.code"
    ).fetchall()]
    conn.close()
    return "\n".join([f"- [{l['code']}] {l['name_th']} (ความเสี่ยง: {l['risk_level']}): {l['description'] or ''}" for l in laws])

SYSTEM_PROMPT = """คุณคือ AI Legal Assistant สำหรับระบบ Thai Law Compliance Management ของบริษัท SYS Steel (โรงงานอุตสาหกรรมเหล็กรีดร้อน)

คุณมีความเชี่ยวชาญด้านกฏหมายไทยที่เกี่ยวข้องกับโรงงานอุตสาหกรรม ได้แก่:
- กฏหมายโรงงาน (พ.ร.บ. โรงงาน พ.ศ. 2535)
- ความปลอดภัยและอาชีวอนามัย
- สิ่งแวดล้อมและมลพิษ
- กฏหมายแรงงาน
- มาตรฐานผลิตภัณฑ์ (มอก.)
- ภาษีและการเงิน
- การค้าและโลจิสติกส์
- CSR และธรรมาภิบาล
- ความมั่นคงปลอดภัยไซเบอร์

กฏหมายในระบบปัจจุบัน:
{laws_context}

โครงสร้างหน่วยงานของ SYS Steel:
- Maptapud Plant: SP-MP, RM-MP, MT-MP, ET, OE
- Huaypong Plant: SP-HP, RM-HP, MT-HP, Eng, DX&IT
- SCM: SCP, LG, IV, QP
- P&A: Gen Pro, Scrap Pro, AC
- Marketing: DOM, EXP, SoPro, MarCom
- Sustainability: PG, Safety, CSR, IA

ระดับความเกี่ยวข้อง: primary (รับผิดชอบหลัก), high (เกี่ยวข้องมาก), medium (เกี่ยวข้องปานกลาง)

=== FORMAT สำหรับการ ลบ/ถอนกฏหมายที่ไม่มีผลบังคับใช้ ===
<law_update>
{{
  "action": "remove_law",
  "law_code": "รหัสกฏหมายที่ต้องการลบ เช่น CSR-001",
  "reason": "เหตุผลที่ลบ เช่น ยังไม่มีผลบังคับใช้ในประเทศไทย"
}}
</law_update>

=== FORMAT สำหรับการ UPDATE กฏหมายที่มีอยู่แล้ว ===
<law_update>
{{
  "action": "update_law",
  "law_code": "รหัสกฏหมายที่มีอยู่แล้ว เช่น LABOR-001",
  "changes": {{"old": "ข้อความเดิม", "new": "ข้อความใหม่"}},
  "summary": "สรุปการเปลี่ยนแปลง",
  "source": "แหล่งอ้างอิง"
}}
</law_update>

=== FORMAT สำหรับการ เพิ่มกฏหมายใหม่ (ต้องมี dept_matrix และ tasks เสมอ) ===
<law_update>
{{
  "action": "add_law",
  "law_code": "รหัสใหม่ เช่น CYBER-001",
  "category_code": "FACTORY/SAFETY/ENV/LABOR/QUALITY/TAX/TRADE/CSRLAW",
  "name_th": "ชื่อกฏหมายภาษาไทย",
  "name_en": "Law name in English",
  "description": "รายละเอียดสำคัญ",
  "effective_date": "YYYY-MM-DD",
  "risk_level": "critical/high/medium/low",
  "penalty_summary": "สรุปบทลงโทษ",
  "source": "แหล่งอ้างอิง",
  "dept_matrix": [
    {{"dept_code": "DX&IT", "relevance": "primary"}},
    {{"dept_code": "OE", "relevance": "high"}},
    {{"dept_code": "IA", "relevance": "high"}}
  ],
  "tasks": [
    {{"dept_code": "DX&IT", "title": "ชื่อ task", "description": "รายละเอียด", "priority": "high/critical/medium"}},
    {{"dept_code": "OE", "title": "ชื่อ task", "description": "รายละเอียด", "priority": "medium"}}
  ]
}}
</law_update>

ตอบเป็นภาษาไทยเป็นหลัก กระชับ ชัดเจน และเป็นประโยชน์"""

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    username: Optional[str] = "anonymous"
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    law_updates: Optional[list] = []

@app.get("/api/chat/provider")
def get_chat_provider():
    """แสดง provider และ model ที่ใช้งานอยู่"""
    p = get_provider()
    model_map = {
        "anthropic":  os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5"),
        "openai":     os.environ.get("OPENAI_MODEL", "gpt-4o"),
        "bedrock":    os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6"),
        "grok":       os.environ.get("GROK_MODEL", "grok-3-mini"),
        "ollama":     os.environ.get("OLLAMA_MODEL", "llama3.2"),
        "openrouter": os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        "demo":       "demo",
    }
    return {"provider": p, "model": model_map.get(p, "unknown")}

class ProviderSwitch(BaseModel):
    provider: str
    model: Optional[str] = None

@app.post("/api/chat/provider")
def set_chat_provider(body: ProviderSwitch):
    """เปลี่ยน provider และ model แบบ runtime (ไม่ต้อง restart)"""
    valid = ["anthropic", "openai", "bedrock", "grok", "ollama", "openrouter"]
    if body.provider not in valid:
        raise HTTPException(400, f"provider ต้องเป็นหนึ่งใน: {valid}")
    os.environ["LLM_PROVIDER"] = body.provider
    model_env = {
        "anthropic": "ANTHROPIC_MODEL", "openai": "OPENAI_MODEL",
        "bedrock": "BEDROCK_MODEL_ID", "grok": "GROK_MODEL",
        "ollama": "OLLAMA_MODEL", "openrouter": "OPENROUTER_MODEL",
    }
    if body.model and body.provider in model_env:
        os.environ[model_env[body.provider]] = body.model
    return {"provider": body.provider, "model": body.model or os.environ.get(model_env.get(body.provider,""), "")}

def _apply_law_updates(conn, reply: str, session_id: str) -> list:
    """Parse และ apply <law_update> blocks จาก LLM reply"""
    import re
    law_updates = []
    for match in re.findall(r'<law_update>(.*?)</law_update>', reply, re.DOTALL):
        try:
            update_data = json.loads(match.strip())
            law_updates.append(update_data)
            action = update_data.get("action")
            if action == "remove_law" and update_data.get("law_code"):
                law_row = conn.execute("SELECT id, name_th FROM laws WHERE code=?", (update_data["law_code"],)).fetchone()
                if law_row:
                    lid = law_row[0]
                    for tbl in ("department_law_matrix","compliance_tasks","law_updates"):
                        conn.execute(f"DELETE FROM {tbl} WHERE law_id=?", (lid,))
                    conn.execute("DELETE FROM laws WHERE id=?", (lid,))
                    conn.commit(); update_data["removed"] = True; update_data["law_name"] = law_row[1]
                else:
                    update_data["removed"] = False; update_data["error"] = "ไม่พบกฏหมายรหัสนี้"
            elif action == "update_law" and update_data.get("law_code"):
                law_row = conn.execute("SELECT id FROM laws WHERE code=?", (update_data["law_code"],)).fetchone()
                if law_row:
                    new_desc = update_data.get("changes", {}).get("new", "")
                    if new_desc:
                        conn.execute("UPDATE laws SET description=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (new_desc, law_row[0]))
                    conn.execute("INSERT INTO law_updates (law_id, update_type, summary, source, agent_run_id) VALUES (?,?,?,?,?)",
                        (law_row[0], "amended", update_data.get("summary",""), update_data.get("source","AI Agent"), session_id))
                    conn.commit()
            elif action == "add_law" and update_data.get("law_code") and update_data.get("name_th"):
                if not conn.execute("SELECT id FROM laws WHERE code=?", (update_data["law_code"],)).fetchone():
                    cat = conn.execute("SELECT id FROM law_categories WHERE code=?", (update_data.get("category_code","CSRLAW"),)).fetchone()
                    r = conn.execute(
                        "INSERT INTO laws (category_id, code, name_th, name_en, description, effective_date, risk_level, penalty_summary, source_url) VALUES (?,?,?,?,?,?,?,?,?)",
                        (cat[0] if cat else 8, update_data["law_code"], update_data["name_th"], update_data.get("name_en",""),
                         update_data.get("description",""), update_data.get("effective_date",""),
                         update_data.get("risk_level","medium"), update_data.get("penalty_summary",""), update_data.get("source","")))
                    new_id = r.lastrowid
                    conn.execute("INSERT INTO law_updates (law_id, update_type, summary, source, agent_run_id) VALUES (?,?,?,?,?)",
                        (new_id, "new", f"เพิ่มกฏหมายใหม่: {update_data['name_th']}", update_data.get("source","AI Agent"), session_id))
                    mc = tc = 0
                    for dm in update_data.get("dept_matrix", []):
                        dr = conn.execute("SELECT id FROM departments WHERE code=?", (dm["dept_code"],)).fetchone()
                        if dr:
                            conn.execute("INSERT OR IGNORE INTO department_law_matrix (department_id, law_id, relevance_level) VALUES (?,?,?)", (dr[0], new_id, dm.get("relevance","medium"))); mc += 1
                    for t in update_data.get("tasks", []):
                        dr = conn.execute("SELECT id FROM departments WHERE code=?", (t["dept_code"],)).fetchone()
                        if dr:
                            conn.execute("INSERT INTO compliance_tasks (law_id, department_id, title, description, priority, status) VALUES (?,?,?,?,?,?)",
                                (new_id, dr[0], t["title"], t.get("description",""), t.get("priority","medium"), "todo")); tc += 1
                    conn.commit(); update_data["added"] = True; update_data["matrix_created"] = mc; update_data["tasks_created"] = tc
        except: pass
    return law_updates


def _build_tool_result_anthropic(calls, results):
    """สร้าง tool_result blocks สำหรับ Anthropic format"""
    return [{"type": "tool_result", "tool_use_id": c["id"], "content": r} for c, r in zip(calls, results)]


def _build_tool_result_openai(raw_message, calls, results):
    """สร้าง messages สำหรับ OpenAI tool calling format"""
    import anthropic as _a
    # raw_message อาจเป็น OpenAI message object
    msgs = [raw_message] if not isinstance(raw_message, dict) else [raw_message]
    for c, r in zip(calls, results):
        msgs.append({"role": "tool", "tool_call_id": c["id"], "content": r})
    return msgs


@app.post("/api/chat")
async def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())[:8]
    username = body.username or "anonymous"
    conn = get_conn()
    laws_ctx = get_laws_context()
    system = SYSTEM_PROMPT.format(laws_context=laws_ctx)

    messages = [{"role": m.role, "content": m.content} for m in (body.history or [])]
    messages.append({"role": "user", "content": body.message})

    reply = ""
    law_updates = []
    provider = get_provider()

    try:
        # ── Agentic loop (tool calling) ────────────────────────────────────────
        MAX_ROUNDS = 5
        for _round in range(MAX_ROUNDS):
            result = call_llm_with_tools(system, messages, TOOLS, TOOLS_OPENAI)

            if result["type"] == "text":
                reply = result["content"]
                break

            # LLM wants to call tools
            calls = result["calls"]
            tool_results = [execute_tool(c["name"], c["input"]) for c in calls]

            # Append tool use + results back into messages (provider-specific format)
            if provider in ("anthropic", "bedrock"):
                raw_content = result.get("raw_content", [])
                # Convert Anthropic content blocks to serializable dicts
                content_dicts = []
                for b in raw_content:
                    if hasattr(b, "type"):
                        if b.type == "tool_use":
                            content_dicts.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
                        elif b.type == "text":
                            content_dicts.append({"type": "text", "text": b.text})
                    else:
                        content_dicts.append(b)
                messages.append({"role": "assistant", "content": content_dicts})
                messages.append({"role": "user", "content": _build_tool_result_anthropic(calls, tool_results)})
            else:
                # OpenAI-compatible
                raw_msg = result.get("raw_message")
                if raw_msg is not None:
                    messages.append(raw_msg)
                for c, r in zip(calls, tool_results):
                    messages.append({"role": "tool", "tool_call_id": c["id"], "content": r})
        else:
            reply = "⚠️ Agent ใช้ tool เกินรอบที่กำหนด กรุณาลองใหม่"

    except ValueError as e:
        if str(e) == "demo":
            reply = "สวัสดีครับ ผมคือ **Thoth-Legal Agent** สำหรับ SYS Steel\n\n⚙️ ขณะนี้อยู่ใน **Demo mode** — กรุณาตั้งค่า `LLM_PROVIDER` ใน `.env`\n\nรองรับ: `anthropic` | `openai` | `bedrock` | `grok` | `ollama` | `openrouter`"
        else:
            raise
    except Exception as e:
        reply = f"⚠️ LLM Error ({provider}): {str(e)}"

    # Apply any law_update blocks in the reply
    law_updates = _apply_law_updates(conn, reply, session_id)
    conn.close()

    # Save session + messages
    conn2 = get_conn()
    title = body.message[:40] + ("…" if len(body.message) > 40 else "")
    conn2.execute(
        "INSERT INTO chat_sessions (session_id, username, title, updated_at) VALUES (?,?,?,CURRENT_TIMESTAMP) "
        "ON CONFLICT(session_id) DO UPDATE SET updated_at=CURRENT_TIMESTAMP",
        (session_id, username, title))
    conn2.execute("INSERT INTO chat_messages (session_id, role, content, law_updates) VALUES (?,?,?,?)",
        (session_id, "user", body.message, "[]"))
    conn2.execute("INSERT INTO chat_messages (session_id, role, content, law_updates) VALUES (?,?,?,?)",
        (session_id, "assistant", reply, json.dumps(law_updates, ensure_ascii=False)))
    conn2.commit(); conn2.close()
    return {"reply": reply, "session_id": session_id, "law_updates": law_updates}

# ── AUTH ──────────────────────────────────────────────────────────────────────
import hashlib, secrets

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def seed_admin():
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?,?,?)",
        ("admin1", hash_pw("adm1219"), "admin"))
    conn.commit(); conn.close()

seed_admin()

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
def login(body: LoginRequest):
    conn = get_conn()
    user = row(conn.execute("SELECT * FROM users WHERE username=?", (body.username,)))
    conn.close()
    if not user or user["password_hash"] != hash_pw(body.password):
        raise HTTPException(401, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    token = f"{user['id']}:{secrets.token_hex(16)}"
    return {"token": token, "username": user["username"], "role": user["role"]}

@app.get("/api/auth/users")
def get_users(x_role: str = Header(None)):
    if x_role != "admin": raise HTTPException(403, "Admin only")
    conn = get_conn()
    result = rows(conn.execute("SELECT id, username, role, created_at FROM users ORDER BY id"))
    conn.close(); return result

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

@app.post("/api/auth/users")
def create_user(body: UserCreate, x_role: str = Header(None)):
    if x_role != "admin": raise HTTPException(403, "Admin only")
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            (body.username, hash_pw(body.password), body.role))
        conn.commit()
    except Exception:
        raise HTTPException(400, "ชื่อผู้ใช้นี้มีอยู่แล้ว")
    conn.close(); return {"success": True}

@app.delete("/api/auth/users/{user_id}")
def delete_user(user_id: int, x_role: str = Header(None)):
    if x_role != "admin": raise HTTPException(403, "Admin only")
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id=? AND username!='admin1'", (user_id,))
    conn.commit(); conn.close(); return {"success": True}

@app.post("/api/auth/users/{user_id}/reset-password")
def reset_password(user_id: int, x_role: str = Header(None)):
    if x_role != "admin": raise HTTPException(403, "Admin only")
    conn = get_conn()
    conn.execute("UPDATE users SET password_hash=? WHERE id=? AND username!='admin1'", (hash_pw("9999"), user_id))
    conn.commit(); conn.close(); return {"success": True}

class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

@app.post("/api/auth/change-password")
def change_password(body: ChangePasswordRequest):
    conn = get_conn()
    user = row(conn.execute("SELECT * FROM users WHERE username=?", (body.username,)))
    if not user or user["password_hash"] != hash_pw(body.old_password):
        conn.close(); raise HTTPException(400, "รหัสผ่านเดิมไม่ถูกต้อง")
    conn.execute("UPDATE users SET password_hash=? WHERE username=?", (hash_pw(body.new_password), body.username))
    conn.commit(); conn.close(); return {"success": True}

# ── CHAT HISTORY ─────────────────────────────────────────────────────────────
@app.get("/api/chat/sessions")
def get_chat_sessions(username: str = "anonymous"):
    conn = get_conn()
    sessions = rows(conn.execute(
        "SELECT session_id, title, created_at, updated_at FROM chat_sessions WHERE username=? ORDER BY updated_at DESC LIMIT 50",
        (username,)
    ))
    conn.close(); return sessions

@app.get("/api/chat/sessions/{session_id}")
def get_chat_session(session_id: str):
    conn = get_conn()
    msgs = rows(conn.execute(
        "SELECT role, content, law_updates, created_at FROM chat_messages WHERE session_id=? ORDER BY created_at ASC",
        (session_id,)
    ))
    for m in msgs:
        try: m["law_updates"] = json.loads(m["law_updates"] or "[]")
        except: m["law_updates"] = []
    conn.close(); return msgs

@app.delete("/api/chat/sessions/{session_id}")
def delete_chat_session(session_id: str):
    conn = get_conn()
    conn.execute("DELETE FROM chat_messages WHERE session_id=?", (session_id,))
    conn.execute("DELETE FROM chat_sessions WHERE session_id=?", (session_id,))
    conn.commit(); conn.close(); return {"success": True}

# ── STATIC FRONTEND ───────────────────────────────────────────────────────────
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
