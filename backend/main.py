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
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

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
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    law_updates: Optional[list] = []

@app.post("/api/chat")
async def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())[:8]
    conn = get_conn()
    laws_ctx = get_laws_context()
    system = SYSTEM_PROMPT.format(laws_context=laws_ctx)

    messages = [{"role": m.role, "content": m.content} for m in (body.history or [])]
    messages.append({"role": "user", "content": body.message})

    reply = ""
    law_updates = []

    # Try Anthropic first, then OpenAI, then fallback
    anthropic_ok = False
    if ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=8096,
                system=system,
                messages=messages
            )
            reply = response.content[0].text
            anthropic_ok = True
        except Exception as e:
            err = str(e)
            # Fall through to OpenAI if credit/auth issue
            if any(x in err for x in ["credit", "balance", "401", "authentication"]):
                anthropic_ok = False
            else:
                reply = f"⚠️ Anthropic API error: {err}"
                anthropic_ok = True  # real error, don't fallback

    if not anthropic_ok and OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system}] + messages,
                max_tokens=8096
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ OpenAI API error: {str(e)}"
    elif not anthropic_ok and not OPENAI_API_KEY:
        # Demo mode - smart keyword-based responses
        msg = body.message.lower()
        if any(k in msg for k in ["อัปเดต","update","ค้นหา","search","ใหม่","เปลี่ยน"]):
            reply = """🔍 **กำลังค้นหาการเปลี่ยนแปลงกฏหมาย...**

จากการตรวจสอบแหล่งข้อมูลล่าสุด (ราชกิจจานุเบกษา, กรมโรงงานอุตสาหกรรม):

**พบการเปลี่ยนแปลงที่น่าสนใจ:**

1. **LABOR-001** - พ.ร.บ. คุ้มครองแรงงาน ฉบับที่ 9 พ.ศ. 2568
   - 🔴 เก่า: ลาคลอด 98 วัน
   - 🟢 ใหม่: ลาคลอด 120 วัน (มีผล 7 ธ.ค. 2568)
   - มีการหารือเพิ่มเติมเรื่องลาบิดา อาจขยายเป็น 30 วัน

2. **SAFETY-001** - กฎกระทรวงความปลอดภัย
   - มีการปรับปรุงมาตรฐาน PPE สำหรับงานเชื่อมโลหะ

⚠️ **หมายเหตุ:** กรุณาตั้งค่า ANTHROPIC_API_KEY หรือ OPENAI_API_KEY เพื่อค้นหาข้อมูลจริงจาก web"""
        elif any(k in msg for k in ["factory","โรงงาน","ใบอนุญาต"]):
            reply = """**พ.ร.บ. โรงงาน พ.ศ. 2535 (แก้ไข พ.ศ. 2562)**

โรงงานเหล็กของ SYS Steel จัดเป็น **โรงงานประเภท 3** เนื่องจาก:
- ใช้เครื่องจักรเกิน 75 แรงม้า
- มีพนักงานเกิน 75 คน

**ข้อกำหนดสำคัญ:**
- ต้องขอใบอนุญาตจาก กรมโรงงานอุตสาหกรรม (กรอ.)
- ใช้เวลา 40-90 วัน
- ต้องมี EIA, แผนความปลอดภัย, แผนผังอาคาร

**บทลงโทษ:** จำคุกสูงสุด 4 ปี และ/หรือปรับสูงสุด 400,000 บาท

**หน่วยงานรับผิดชอบ:** OE (Operational Excellence), IA (Internal Audit)"""
        elif any(k in msg for k in ["safety","ความปลอดภัย","ppe","อุบัติเหตุ"]):
            reply = """**กฏหมายความปลอดภัยและอาชีวอนามัย**

**พ.ร.บ. ความปลอดภัยฯ พ.ศ. 2554:**
- บังคับมีเจ้าหน้าที่ความปลอดภัย (จป.) ทุกระดับ
- จป. วิชาชีพ: ปริญญาตรี + ประสบการณ์ > 5 ปี
- ต้องรายงานอุบัติเหตุร้ายแรงภายใน 7 วัน

**PPE ที่บังคับสำหรับโรงงานเหล็ก:**
- หน้ากากกันความร้อน + แว่นตาป้องกัน
- อุปกรณ์ลดเสียง (พื้นที่ > 85 dB)
- เครื่องช่วยหายใจ (พื้นที่ฝุ่น/ก๊าซ)
- รองเท้านิรภัย + ถุงมือกันความร้อน

**หน่วยงานรับผิดชอบ:** Safety Department (primary)"""
        elif any(k in msg for k in ["สิ่งแวดล้อม","env","cems","มลพิษ"]):
            reply = """**กฏหมายสิ่งแวดล้อม**

**CEMS (ระบบตรวจวัดมลพิษต่อเนื่อง):**
- บังคับสำหรับโรงงานเหล็กขนาดใหญ่
- ต้องเชื่อมต่อ real-time กับ กรมควบคุมมลพิษ 24/7
- ค่ามาตรฐาน: ฝุ่นละออง ≤ 60 มก./ลบ.ม.

**บทลงโทษ:**
- ละเมิดมาตรฐาน: ปรับสูงสุด 1,500,000 บาท + ค่าปรับรายวัน
- ไม่ติดตั้ง CEMS: สั่งแก้ไข + บทลงโทษเพิ่มเติม

**หน่วยงานรับผิดชอบ:** Safety (primary), ET/Eng (high)"""
        else:
            reply = f"""สวัสดีครับ ผมคือ AI Legal Assistant สำหรับระบบ Thai Law Compliance ของ SYS Steel

ผมสามารถช่วยคุณได้เกี่ยวกับ:
- 📋 **รายละเอียดกฏหมาย** - ถามเกี่ยวกับกฏหมายใดก็ได้ในระบบ
- 🔍 **ค้นหาการเปลี่ยนแปลง** - พิมพ์ "อัปเดตกฏหมาย" หรือ "ค้นหากฏหมายใหม่"
- 🏭 **ผลกระทบต่อหน่วยงาน** - ถามว่ากฏหมายใดเกี่ยวข้องกับแผนกไหน
- ⚠️ **บทลงโทษ** - ถามเกี่ยวกับโทษและค่าปรับ

ตัวอย่างคำถาม:
- "พ.ร.บ. โรงงานกำหนดอะไรบ้าง?"
- "Safety ต้องทำอะไรตามกฏหมาย?"
- "อัปเดตกฏหมายแรงงานล่าสุด"

⚙️ *ตั้งค่า ANTHROPIC_API_KEY หรือ OPENAI_API_KEY เพื่อใช้ AI จริง*"""

    # Parse law_updates from reply
    import re
    update_matches = re.findall(r'<law_update>(.*?)</law_update>', reply, re.DOTALL)
    for match in update_matches:
        try:
            update_data = json.loads(match.strip())
            law_updates.append(update_data)
            action = update_data.get("action")

            # Auto-apply: remove law
            if action == "remove_law" and update_data.get("law_code"):
                law_row = conn.execute("SELECT id, name_th FROM laws WHERE code=?", (update_data["law_code"],)).fetchone()
                if law_row:
                    lid = law_row[0]
                    conn.execute("DELETE FROM department_law_matrix WHERE law_id=?", (lid,))
                    conn.execute("DELETE FROM compliance_tasks WHERE law_id=?", (lid,))
                    conn.execute("DELETE FROM law_updates WHERE law_id=?", (lid,))
                    conn.execute("DELETE FROM laws WHERE id=?", (lid,))
                    conn.commit()
                    update_data["removed"] = True
                    update_data["law_name"] = law_row[1]
                else:
                    update_data["removed"] = False
                    update_data["error"] = "ไม่พบกฏหมายรหัสนี้ในระบบ"

            # Auto-apply: update existing law
            elif action == "update_law" and update_data.get("law_code"):
                law_row = conn.execute("SELECT id FROM laws WHERE code=?", (update_data["law_code"],)).fetchone()
                if law_row:
                    new_desc = update_data.get("changes", {}).get("new", "")
                    if new_desc:
                        conn.execute("UPDATE laws SET description=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (new_desc, law_row[0]))
                    conn.execute("INSERT INTO law_updates (law_id, update_type, summary, source, agent_run_id) VALUES (?,?,?,?,?)",
                        (law_row[0], "amended", update_data.get("summary",""), update_data.get("source","AI Agent"), session_id))
                    conn.commit()

            # Auto-apply: add new law
            elif action == "add_law" and update_data.get("law_code") and update_data.get("name_th"):
                # Check not duplicate
                existing = conn.execute("SELECT id FROM laws WHERE code=?", (update_data["law_code"],)).fetchone()
                if not existing:
                    cat = conn.execute("SELECT id FROM law_categories WHERE code=?", (update_data.get("category_code","CSRLAW"),)).fetchone()
                    cat_id = cat[0] if cat else 8
                    r = conn.execute(
                        "INSERT INTO laws (category_id, code, name_th, name_en, description, effective_date, risk_level, penalty_summary, source_url) VALUES (?,?,?,?,?,?,?,?,?)",
                        (cat_id, update_data["law_code"], update_data["name_th"], update_data.get("name_en",""),
                         update_data.get("description",""), update_data.get("effective_date",""),
                         update_data.get("risk_level","medium"), update_data.get("penalty_summary",""),
                         update_data.get("source",""))
                    )
                    new_law_id = r.lastrowid
                    conn.execute("INSERT INTO law_updates (law_id, update_type, summary, source, agent_run_id) VALUES (?,?,?,?,?)",
                        (new_law_id, "new", f"เพิ่มกฏหมายใหม่: {update_data['name_th']}", update_data.get("source","AI Agent"), session_id))

                    # Auto-create department matrix
                    matrix_count = 0
                    for dm in update_data.get("dept_matrix", []):
                        dept_row = conn.execute("SELECT id FROM departments WHERE code=?", (dm["dept_code"],)).fetchone()
                        if dept_row:
                            conn.execute("INSERT OR IGNORE INTO department_law_matrix (department_id, law_id, relevance_level) VALUES (?,?,?)",
                                (dept_row[0], new_law_id, dm.get("relevance", "medium")))
                            matrix_count += 1

                    # Auto-create kanban tasks (todo)
                    task_count = 0
                    for t in update_data.get("tasks", []):
                        dept_row = conn.execute("SELECT id FROM departments WHERE code=?", (t["dept_code"],)).fetchone()
                        if dept_row:
                            conn.execute("INSERT INTO compliance_tasks (law_id, department_id, title, description, priority, status) VALUES (?,?,?,?,?,?)",
                                (new_law_id, dept_row[0], t["title"], t.get("description",""), t.get("priority","medium"), "todo"))
                            task_count += 1

                    conn.commit()
                    update_data["added"] = True
                    update_data["matrix_created"] = matrix_count
                    update_data["tasks_created"] = task_count
        except:
            pass

    conn.close()
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

# ── STATIC FRONTEND ───────────────────────────────────────────────────────────
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
