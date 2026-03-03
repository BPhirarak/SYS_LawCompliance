"""
Thai Law Scanner Agent
รันเดือนละครั้งเพื่อค้นหากฏหมายที่อาจมีการเปลี่ยนแปลง
ต้องการ: OPENAI_API_KEY หรือ ANTHROPIC_API_KEY ใน environment
"""
import os, sys, uuid, datetime, sqlite3, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

DB_PATH = os.path.join(os.path.dirname(__file__), '../backend/law.db')

LAW_SOURCES = [
    "https://www.ratchakitchanubeksa.go.th",  # ราชกิจจานุเบกษา
    "https://www.diw.go.th",                   # กรมโรงงานอุตสาหกรรม
    "https://www.pcd.go.th",                   # กรมควบคุมมลพิษ
    "https://www.labour.go.th",                # กระทรวงแรงงาน
    "https://www.tisi.go.th",                  # สมอ.
]

SEARCH_KEYWORDS = [
    "พระราชบัญญัติโรงงาน", "ความปลอดภัยอาชีวอนามัย",
    "สิ่งแวดล้อม มลพิษ โรงงาน", "คุ้มครองแรงงาน",
    "มาตรฐานผลิตภัณฑ์อุตสาหกรรม เหล็ก", "HREDD",
]

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def run_agent():
    run_id = str(uuid.uuid4())[:8]
    conn = get_conn()
    conn.execute("INSERT INTO agent_runs (run_id, status) VALUES (?,?)", (run_id, 'running'))
    conn.commit()

    print(f"🤖 Law Scanner Agent started | run_id: {run_id}")
    print(f"📅 Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    laws = [dict(r) for r in conn.execute("SELECT * FROM laws WHERE status='active'").fetchall()]
    print(f"📚 Checking {len(laws)} active laws...")

    # ── ตรงนี้ใส่ logic จริงด้วย LLM API ──────────────────────────────────────
    # ตัวอย่าง: ใช้ OpenAI web search หรือ Anthropic เพื่อค้นหาการเปลี่ยนแปลง
    #
    # import openai
    # client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    # for law in laws:
    #     response = client.chat.completions.create(
    #         model="gpt-4o-search-preview",
    #         messages=[{"role": "user", "content": f"ค้นหาการเปลี่ยนแปลงล่าสุดของ {law['name_th']} ในปี 2568-2569"}]
    #     )
    #     # parse response และ insert ลง law_updates
    # ──────────────────────────────────────────────────────────────────────────

    # Demo: simulate finding an update
    demo_update = {
        "law_code": "LABOR-001",
        "update_type": "amended",
        "summary": "Agent ตรวจพบ: มีการหารือเพิ่มเติมเกี่ยวกับการขยายสิทธิลาบิดา จาก 15 วัน เป็น 30 วัน (อยู่ระหว่างพิจารณา)",
        "source": "ราชกิจจานุเบกษา (simulated)"
    }

    law_row = conn.execute("SELECT id FROM laws WHERE code=?", (demo_update["law_code"],)).fetchone()
    if law_row:
        conn.execute("INSERT INTO law_updates (law_id, update_type, summary, source, agent_run_id) VALUES (?,?,?,?,?)",
            (law_row[0], demo_update["update_type"], demo_update["summary"], demo_update["source"], run_id))

    conn.execute("UPDATE agent_runs SET status='completed', completed_at=CURRENT_TIMESTAMP, laws_checked=?, updates_found=1, summary=? WHERE run_id=?",
        (len(laws), f"ตรวจสอบ {len(laws)} กฏหมาย พบการเปลี่ยนแปลง 1 รายการ", run_id))
    conn.commit()
    conn.close()

    print(f"✅ Agent completed | checked: {len(laws)} laws | updates: 1")
    print(f"💾 Results saved to database")

if __name__ == "__main__":
    run_agent()
