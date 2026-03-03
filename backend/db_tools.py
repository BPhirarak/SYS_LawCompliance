"""
DB Tools for Thoth-Legal Agent
LLM สามารถเรียก function เหล่านี้เพื่อ query ข้อมูลจาก SQLite ได้โดยตรง
"""
import json
from database import get_conn

# ── Tool Definitions (Anthropic / OpenAI format) ──────────────────────────────

TOOLS = [
    {
        "name": "query_tasks",
        "description": (
            "ดึงรายการ compliance tasks จาก Kanban board "
            "กรองได้ตาม status (todo/in_progress/done), priority (critical/high/medium/low), "
            "department_code, law_code หรือ keyword ในชื่อ task"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status":          {"type": "string", "enum": ["todo","in_progress","done","all"], "description": "สถานะ task, ใช้ 'all' เพื่อดูทุกสถานะ"},
                "priority":        {"type": "string", "enum": ["critical","high","medium","low","all"], "description": "ระดับความสำคัญ"},
                "department_code": {"type": "string", "description": "รหัสหน่วยงาน เช่น PROD, QA, HR"},
                "law_code":        {"type": "string", "description": "รหัสกฎหมาย เช่น PDPA, ISO45001"},
                "keyword":         {"type": "string", "description": "คำค้นหาในชื่อหรือรายละเอียด task"},
                "limit":           {"type": "integer", "description": "จำนวนสูงสุดที่ต้องการ (default 20)"}
            },
            "required": []
        }
    },
    {
        "name": "query_laws",
        "description": (
            "ดึงรายการกฎหมายในระบบ กรองได้ตาม category_code, risk_level, "
            "status หรือ keyword ในชื่อกฎหมาย"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category_code": {"type": "string", "description": "รหัสหมวดหมู่ เช่น LABOR, ENV, CYBER, SAFETY"},
                "risk_level":    {"type": "string", "enum": ["critical","high","medium","low","all"]},
                "status":        {"type": "string", "enum": ["active","inactive","all"]},
                "keyword":       {"type": "string", "description": "คำค้นหาในชื่อกฎหมาย"},
                "limit":         {"type": "integer"}
            },
            "required": []
        }
    },
    {
        "name": "query_departments",
        "description": "ดึงรายชื่อหน่วยงานทั้งหมดหรือค้นหาตาม keyword",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "คำค้นหาในชื่อหน่วยงาน"}
            },
            "required": []
        }
    },
    {
        "name": "query_matrix",
        "description": (
            "ดึงข้อมูล matrix ความสัมพันธ์ระหว่างหน่วยงานกับกฎหมาย "
            "กรองได้ตาม department_code, law_code หรือ relevance_level"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "department_code": {"type": "string"},
                "law_code":        {"type": "string"},
                "relevance_level": {"type": "string", "enum": ["high","medium","low","all"]}
            },
            "required": []
        }
    },
    {
        "name": "query_dashboard",
        "description": (
            "ดึงสรุปภาพรวมของระบบ: จำนวน tasks แยกตาม status/priority, "
            "กฎหมาย risk สูง, หน่วยงานที่มี overdue tasks"
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# OpenAI format (แปลงจาก Anthropic format)
TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"]
        }
    }
    for t in TOOLS
]

# ── Tool Executor ─────────────────────────────────────────────────────────────

def execute_tool(name: str, args: dict) -> str:
    """รัน tool และคืนผลลัพธ์เป็น JSON string"""
    try:
        if name == "query_tasks":    return _query_tasks(**args)
        if name == "query_laws":     return _query_laws(**args)
        if name == "query_departments": return _query_departments(**args)
        if name == "query_matrix":   return _query_matrix(**args)
        if name == "query_dashboard": return _query_dashboard()
        return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _query_tasks(status="all", priority="all", department_code=None,
                 law_code=None, keyword=None, limit=20):
    conn = get_conn()
    sql = """
        SELECT ct.id, ct.title, ct.description, ct.status, ct.priority,
               ct.assignee, ct.due_date, ct.plan,
               d.code AS dept_code, d.name_th AS dept_name,
               l.code AS law_code, l.name_th AS law_name
        FROM compliance_tasks ct
        LEFT JOIN departments d ON ct.department_id = d.id
        LEFT JOIN laws l ON ct.law_id = l.id
        WHERE 1=1
    """
    params = []
    if status and status != "all":
        sql += " AND ct.status = ?"; params.append(status)
    if priority and priority != "all":
        sql += " AND ct.priority = ?"; params.append(priority)
    if department_code:
        sql += " AND d.code = ?"; params.append(department_code)
    if law_code:
        sql += " AND l.code = ?"; params.append(law_code)
    if keyword:
        sql += " AND (ct.title LIKE ? OR ct.description LIKE ?)";
        params += [f"%{keyword}%", f"%{keyword}%"]
    sql += f" ORDER BY CASE ct.priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, ct.created_at DESC LIMIT ?"
    params.append(min(limit or 20, 50))
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return json.dumps({"count": len(rows), "tasks": rows}, ensure_ascii=False)


def _query_laws(category_code=None, risk_level="all", status="active", keyword=None, limit=30):
    conn = get_conn()
    sql = """
        SELECT l.code, l.name_th, l.name_en, l.risk_level, l.status,
               l.effective_date, l.penalty_summary, l.description,
               lc.code AS category_code, lc.name_th AS category_name
        FROM laws l
        LEFT JOIN law_categories lc ON l.category_id = lc.id
        WHERE 1=1
    """
    params = []
    if status and status != "all":
        sql += " AND l.status = ?"; params.append(status)
    if risk_level and risk_level != "all":
        sql += " AND l.risk_level = ?"; params.append(risk_level)
    if category_code:
        sql += " AND lc.code = ?"; params.append(category_code)
    if keyword:
        sql += " AND (l.name_th LIKE ? OR l.name_en LIKE ? OR l.description LIKE ?)";
        params += [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
    sql += f" ORDER BY CASE l.risk_level WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END LIMIT ?"
    params.append(min(limit or 30, 100))
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return json.dumps({"count": len(rows), "laws": rows}, ensure_ascii=False)


def _query_departments(keyword=None):
    conn = get_conn()
    sql = "SELECT code, name_th, name_en FROM departments WHERE 1=1"
    params = []
    if keyword:
        sql += " AND (name_th LIKE ? OR name_en LIKE ? OR code LIKE ?)";
        params += [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
    sql += " ORDER BY name_th"
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return json.dumps({"count": len(rows), "departments": rows}, ensure_ascii=False)


def _query_matrix(department_code=None, law_code=None, relevance_level="all"):
    conn = get_conn()
    sql = """
        SELECT d.code AS dept_code, d.name_th AS dept_name,
               l.code AS law_code, l.name_th AS law_name,
               m.relevance_level, l.risk_level
        FROM department_law_matrix m
        JOIN departments d ON m.department_id = d.id
        JOIN laws l ON m.law_id = l.id
        WHERE 1=1
    """
    params = []
    if department_code:
        sql += " AND d.code = ?"; params.append(department_code)
    if law_code:
        sql += " AND l.code = ?"; params.append(law_code)
    if relevance_level and relevance_level != "all":
        sql += " AND m.relevance_level = ?"; params.append(relevance_level)
    sql += " ORDER BY d.name_th, l.name_th LIMIT 100"
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return json.dumps({"count": len(rows), "matrix": rows}, ensure_ascii=False)


def _query_dashboard():
    conn = get_conn()
    # Task summary
    task_summary = {}
    for row in conn.execute("SELECT status, priority, COUNT(*) as cnt FROM compliance_tasks GROUP BY status, priority"):
        key = f"{row['status']}_{row['priority']}"
        task_summary[key] = row['cnt']

    # Total by status
    status_totals = {r['status']: r['cnt'] for r in conn.execute(
        "SELECT status, COUNT(*) as cnt FROM compliance_tasks GROUP BY status")}

    # Critical/high todo+in_progress
    urgent = [dict(r) for r in conn.execute("""
        SELECT ct.title, ct.priority, ct.status, ct.due_date,
               d.name_th AS dept_name, l.name_th AS law_name
        FROM compliance_tasks ct
        LEFT JOIN departments d ON ct.department_id = d.id
        LEFT JOIN laws l ON ct.law_id = l.id
        WHERE ct.priority IN ('critical','high') AND ct.status != 'done'
        ORDER BY CASE ct.priority WHEN 'critical' THEN 1 ELSE 2 END
        LIMIT 10
    """)]

    # Laws by risk
    risk_summary = {r['risk_level']: r['cnt'] for r in conn.execute(
        "SELECT risk_level, COUNT(*) as cnt FROM laws WHERE status='active' GROUP BY risk_level")}

    # Overdue (due_date < today and not done)
    overdue = [dict(r) for r in conn.execute("""
        SELECT ct.title, ct.due_date, d.name_th AS dept_name
        FROM compliance_tasks ct
        LEFT JOIN departments d ON ct.department_id = d.id
        WHERE ct.due_date < date('now') AND ct.status != 'done' AND ct.due_date != ''
        ORDER BY ct.due_date LIMIT 10
    """)]

    conn.close()
    return json.dumps({
        "status_totals": status_totals,
        "task_by_status_priority": task_summary,
        "urgent_tasks": urgent,
        "laws_by_risk": risk_summary,
        "overdue_tasks": overdue
    }, ensure_ascii=False)
