from database import get_conn, init_db

init_db()
conn = get_conn()

# ── DEPARTMENTS (โครงสร้างองค์กรจริง SYS Steel) ──────────────────────────────
departments = [
    # Maptapud Plant
    ("SP-MP",     "Steel Plant - MP",                "Steel Plant - MP"),
    ("RM-MP",     "Rolling Mill - MP",               "Rolling Mill - MP"),
    ("MT-MP",     "Maintenance - MP",                "Maintenance - MP"),
    ("ET",        "Engineering & Technology",        "Engineering & Technology"),
    ("OE",        "Operational Excellence",          "Operational Excellence"),
    # Huaypong Plant
    ("SP-HP",     "Steel Plant - HP",                "Steel Plant - HP"),
    ("RM-HP",     "Rolling Mill - HP",               "Rolling Mill - HP"),
    ("MT-HP",     "Maintenance - HP",                "Maintenance - HP"),
    ("Eng",       "Engineering",                     "Engineering"),
    ("DX&IT",     "Digital Transformation & IT",     "Digital Transformation & IT"),
    # Supply Chain Management
    ("SCP",       "Supply Chain Planning",           "Supply Chain Planning"),
    ("LG",        "Logistic Management",             "Logistic Management"),
    ("IV",        "Inventory Management",            "Inventory Management"),
    ("QP",        "Quality Promotion / Assurance",   "Quality Promotion / Assurance"),
    # Procurement & Accounting
    ("Gen Pro",   "General Procurement",             "General Procurement"),
    ("Scrap Pro", "Scrap Procurement",               "Scrap Procurement"),
    ("AC",        "Accounting",                      "Accounting"),
    # Marketing
    ("DOM",       "Domestic & Dealer Sales",         "Domestic & Dealer Sales"),
    ("EXP",       "Export Sales",                    "Export Sales"),
    ("SoPro",     "Solution & Project Sales",        "Solution & Project Sales"),
    ("MarCom",    "Marketing Communication",         "Marketing Communication"),
    # Sustainability Management
    ("PG",        "Personnel & General Affair",      "Personnel & General Affair"),
    ("Safety",    "Safety",                          "Safety"),
    ("CSR",       "Corporate Social Responsibility", "Corporate Social Responsibility"),
    ("IA",        "Internal Audit & Control",        "Internal Audit & Control"),
]
conn.executemany("INSERT OR IGNORE INTO departments (code, name_th, name_en) VALUES (?,?,?)", departments)

# ── CATEGORIES ────────────────────────────────────────────────────────────────
categories = [
    ("FACTORY", "ใบอนุญาตโรงงาน",              "Factory License"),
    ("SAFETY",  "ความปลอดภัยและอาชีวอนามัย",   "Safety & Occupational Health"),
    ("ENV",     "สิ่งแวดล้อมและมลพิษ",          "Environment & Pollution"),
    ("LABOR",   "กฏหมายแรงงาน",                 "Labor Law"),
    ("QUALITY", "มาตรฐานการผลิตและคุณภาพ",      "Production Standards & Quality"),
    ("TAX",     "การเงินและภาษี",               "Finance & Tax"),
    ("TRADE",   "การค้าและโลจิสติกส์",          "Trade & Logistics"),
    ("CSRLAW",  "ความรับผิดชอบต่อสังคม",        "CSR & Governance"),
]
conn.executemany("INSERT OR IGNORE INTO law_categories (code, name_th, name_en) VALUES (?,?,?)", categories)
conn.commit()

def cat_id(code):
    return conn.execute("SELECT id FROM law_categories WHERE code=?", (code,)).fetchone()[0]

# ── LAWS ──────────────────────────────────────────────────────────────────────
laws = [
    ("FACTORY","FACTORY-001","พระราชบัญญัติโรงงาน พ.ศ. 2535 (แก้ไข พ.ศ. 2562)","Factory Act B.E. 2535 (amended 2562)","กำหนดการขอใบอนุญาตโรงงาน 3 ประเภท โรงงานเหล็กส่วนใหญ่เป็นประเภท 3 ต้องขอใบอนุญาตจาก กรอ.","2562-05-27","critical","จำคุกสูงสุด 4 ปี และ/หรือปรับสูงสุด 400,000 บาท"),
    ("FACTORY","FACTORY-002","กฎกระทรวงกำหนดประเภท ชนิด และขนาดของโรงงาน","Ministerial Regulation on Factory Classification","จำแนกโรงงานเป็น 3 ประเภทตามขนาดเครื่องจักรและจำนวนพนักงาน","2562-01-01","high","ปรับสูงสุด 200,000 บาท"),
    ("SAFETY","SAFETY-001","พระราชบัญญัติความปลอดภัย อาชีวอนามัย และสภาพแวดล้อมในการทำงาน พ.ศ. 2554","Occupational Safety, Health and Environment Act B.E. 2554","กำหนดมาตรฐานความปลอดภัยในสถานที่ทำงาน PPE การรายงานอุบัติเหตุ","2554-07-16","critical","ปรับสูงสุด 200,000 บาท + จำคุก"),
    ("SAFETY","SAFETY-002","กฎกระทรวงว่าด้วยการจัดให้มีเจ้าหน้าที่ความปลอดภัยในการทำงาน พ.ศ. 2565","Ministerial Regulation on Safety Officers B.E. 2565","กำหนดให้โรงงานเหล็กต้องมีเจ้าหน้าที่ความปลอดภัยระดับบังคับบัญชา เทคนิค และวิชาชีพ","2565-08-16","high","ปรับสูงสุด 50,000 บาท"),
    ("ENV","ENV-001","พระราชบัญญัติส่งเสริมและรักษาคุณภาพสิ่งแวดล้อมแห่งชาติ พ.ศ. 2535","National Environmental Quality Promotion and Conservation Act B.E. 2535","กำหนดมาตรฐานการปล่อยมลพิษทางอากาศ น้ำ และดิน บังคับติดตั้ง CEMS","2535-04-04","critical","ปรับสูงสุด 1,500,000 บาท + ค่าปรับรายวัน"),
    ("ENV","ENV-002","ระบบตรวจวัดการปล่อยมลพิษต่อเนื่อง (CEMS)","Continuous Emission Monitoring System (CEMS)","โรงงานเหล็กขนาดใหญ่ต้องติดตั้ง CEMS เชื่อมต่อกับระบบติดตามของรัฐบาล 24/7","2562-01-01","high","สั่งแก้ไข + บทลงโทษเพิ่มเติม"),
    ("LABOR","LABOR-001","พระราชบัญญัติคุ้มครองแรงงาน พ.ศ. 2541 (ฉบับที่ 9 พ.ศ. 2568)","Labor Protection Act B.E. 2541 (Amendment No.9 B.E. 2568)","ขยายสิทธิลาคลอด 120 วัน ลาดูแลภรรยาคลอด 15 วัน ลาดูแลบุตรป่วย 15 วัน/ปี","2568-12-07","high","ปรับสูงสุด 400,000 บาทต่อการละเมิดแต่ละครั้ง"),
    ("LABOR","LABOR-002","ประกาศค่าแรงขั้นต่ำ พ.ศ. 2568","Minimum Wage Announcement B.E. 2568","กรุงเทพฯ 400 บาท/วัน ปริมณฑล 370-399 บาท/วัน จังหวัดอื่น 337-369 บาท/วัน","2568-07-01","medium","ปรับสูงสุด 100,000 บาท"),
    ("QUALITY","QUALITY-001","มาตรฐานผลิตภัณฑ์อุตสาหกรรม (มอก.) สำหรับเหล็ก 22 ฉบับ","Thai Industrial Standards (TIS) for Steel Products","บังคับรับรอง มอก. 22 ฉบับ ติดเครื่องหมาย QR Code สำหรับผลิตภัณฑ์เหล็กทุกประเภท","2560-01-01","critical","ห้ามจำหน่าย + ยึดสินค้า + โทษอาญา"),
    ("TAX","TAX-001","ประมวลรัษฎากร - ภาษีเงินได้นิติบุคคล","Revenue Code - Corporate Income Tax","อัตราภาษีเงินได้นิติบุคคล 0-20% ตามระดับกำไร","2535-01-01","medium","ปรับ + เบี้ยปรับ + เงินเพิ่ม"),
    ("TAX","TAX-002","Global Minimum Tax 15% พ.ศ. 2568","Global Minimum Tax 15% B.E. 2568","บริษัทข้ามชาติที่มีรายได้เกิน EUR 750 ล้าน ต้องเสียภาษีขั้นต่ำ 15%","2568-01-01","medium","ภาษีเพิ่มเติม"),
    ("TAX","TAX-003","Transfer Pricing - กฎหมายราคาโอน","Transfer Pricing Regulations","บริษัทที่มีรายได้เกิน 200 ล้านบาทต้องจัดทำเอกสาร Transfer Pricing","2564-01-01","medium","ปรับ 200,000 บาท/ครั้ง"),
    ("TRADE","TRADE-001","ระบบ National Single Window (NSW) พ.ศ. 2568","National Single Window (NSW) B.E. 2568","บังคับใช้ระบบ NSW สำหรับการนำเข้า-ส่งออกทุกประเภทตั้งแต่ พ.ศ. 2568","2568-01-01","medium","ล่าช้าในการผ่านพิธีการ"),
    ("CSRLAW","CSR-001","ร่างพระราชบัญญัติ HREDD พ.ศ. 2568","Human Rights and Environmental Due Diligence (HREDD) Act B.E. 2568","บริษัทที่มีรายได้เกิน 500 ล้านบาทต้องตรวจสอบห่วงโซ่อุปทานด้านสิทธิมนุษยชนและสิ่งแวดล้อม","2568-01-01","high","ปรับ 500,000 - 5,000,000 บาท"),
    ("CSRLAW","CSR-002","พระราชบัญญัติบริษัทมหาชนจำกัด พ.ศ. 2535 - ธรรมาภิบาล","Public Company Act B.E. 2535 - Corporate Governance","กำหนดให้คณะกรรมการรับผิดชอบต่อการปฏิบัติตามกฎหมายสิ่งแวดล้อมและความปลอดภัย","2535-04-05","medium","กรรมการรับผิดชอบส่วนตัว"),
]
for l in laws:
    conn.execute("INSERT OR IGNORE INTO laws (category_id,code,name_th,name_en,description,effective_date,risk_level,penalty_summary) VALUES (?,?,?,?,?,?,?,?)",
        (cat_id(l[0]),l[1],l[2],l[3],l[4],l[5],l[6],l[7]))
conn.commit()

def dept_id(code):
    r = conn.execute("SELECT id FROM departments WHERE code=?", (code,)).fetchone()
    return r[0] if r else None

def law_id(code):
    r = conn.execute("SELECT id FROM laws WHERE code=?", (code,)).fetchone()
    return r[0] if r else None

# ── DEPARTMENT-LAW MATRIX (mapped to real org structure) ─────────────────────
matrix = [
    # FACTORY-001: ใบอนุญาตโรงงาน
    ("OE","FACTORY-001","primary"), ("IA","FACTORY-001","primary"),
    ("SP-MP","FACTORY-001","high"), ("SP-HP","FACTORY-001","high"),
    ("ET","FACTORY-001","high"), ("Eng","FACTORY-001","high"),
    ("PG","FACTORY-001","medium"),
    # FACTORY-002
    ("OE","FACTORY-002","primary"), ("ET","FACTORY-002","high"), ("Eng","FACTORY-002","high"),
    # SAFETY-001: ความปลอดภัย
    ("Safety","SAFETY-001","primary"),
    ("SP-MP","SAFETY-001","high"), ("RM-MP","SAFETY-001","high"), ("MT-MP","SAFETY-001","high"),
    ("SP-HP","SAFETY-001","high"), ("RM-HP","SAFETY-001","high"), ("MT-HP","SAFETY-001","high"),
    ("PG","SAFETY-001","medium"), ("OE","SAFETY-001","medium"),
    # SAFETY-002: เจ้าหน้าที่ความปลอดภัย
    ("Safety","SAFETY-002","primary"), ("PG","SAFETY-002","high"),
    ("SP-MP","SAFETY-002","medium"), ("SP-HP","SAFETY-002","medium"),
    # ENV-001: สิ่งแวดล้อม
    ("Safety","ENV-001","primary"), ("CSR","ENV-001","primary"),
    ("SP-MP","ENV-001","high"), ("SP-HP","ENV-001","high"),
    ("ET","ENV-001","high"), ("OE","ENV-001","medium"),
    # ENV-002: CEMS
    ("Safety","ENV-002","primary"), ("ET","ENV-002","high"), ("Eng","ENV-002","high"),
    ("SP-MP","ENV-002","medium"), ("SP-HP","ENV-002","medium"),
    # LABOR-001: คุ้มครองแรงงาน
    ("PG","LABOR-001","primary"), ("AC","LABOR-001","high"), ("IA","LABOR-001","medium"),
    # LABOR-002: ค่าแรงขั้นต่ำ
    ("PG","LABOR-002","primary"), ("AC","LABOR-002","high"),
    # QUALITY-001: มอก.
    ("QP","QUALITY-001","primary"),
    ("SP-MP","QUALITY-001","high"), ("RM-MP","QUALITY-001","high"),
    ("SP-HP","QUALITY-001","high"), ("RM-HP","QUALITY-001","high"),
    ("OE","QUALITY-001","medium"),
    # TAX-001
    ("AC","TAX-001","primary"), ("IA","TAX-001","high"),
    # TAX-002
    ("AC","TAX-002","primary"), ("IA","TAX-002","high"),
    # TAX-003
    ("AC","TAX-003","primary"), ("IA","TAX-003","high"),
    # TRADE-001: NSW
    ("LG","TRADE-001","primary"), ("SCP","TRADE-001","high"),
    ("Gen Pro","TRADE-001","high"), ("Scrap Pro","TRADE-001","medium"),
    # CSR-001: HREDD
    ("CSR","CSR-001","primary"), ("PG","CSR-001","high"),
    ("LG","CSR-001","medium"), ("Gen Pro","CSR-001","medium"),
    # CSR-002: ธรรมาภิบาล
    ("CSR","CSR-002","primary"), ("IA","CSR-002","high"), ("AC","CSR-002","medium"),
]
for d, l, level in matrix:
    did, lid = dept_id(d), law_id(l)
    if did and lid:
        conn.execute("INSERT OR IGNORE INTO department_law_matrix (department_id,law_id,relevance_level) VALUES (?,?,?)", (did,lid,level))
conn.commit()

# ── SAMPLE TASKS ──────────────────────────────────────────────────────────────
tasks = [
    ("FACTORY-001","OE","ตรวจสอบและต่ออายุใบอนุญาตโรงงานประเภท 3","ตรวจสอบสถานะใบอนุญาตโรงงาน และดำเนินการต่ออายุก่อนหมดอายุ","critical","todo",None,None,None,None),
    ("SAFETY-001","Safety","จัดทำแผนความปลอดภัยและ PPE ประจำปี","ทบทวนและปรับปรุงแผนความปลอดภัย จัดหา PPE ให้ครบตามมาตรฐาน","high","doing","นายสมชาย ใจดี","ดำเนินการตรวจสอบ PPE ทุกแผนก และจัดซื้อเพิ่มเติมตามที่ขาด","2026-03-31",None),
    ("SAFETY-002","Safety","แต่งตั้งเจ้าหน้าที่ความปลอดภัยระดับวิชาชีพ","ดำเนินการแต่งตั้งและฝึกอบรมเจ้าหน้าที่ความปลอดภัยตามกฎกระทรวง พ.ศ. 2565","high","todo",None,None,None,None),
    ("ENV-001","Safety","ตรวจวัดและรายงานมลพิษทางอากาศประจำไตรมาส","ดำเนินการตรวจวัดค่ามลพิษและส่งรายงานต่อกรมควบคุมมลพิษ","high","done","นางสาวมาลี สะอาด",None,None,"2026-01-15"),
    ("ENV-002","ET","ติดตั้งระบบ CEMS และเชื่อมต่อกับระบบรัฐบาล","ติดตั้ง Continuous Emission Monitoring System และเชื่อมต่อ real-time กับ กรอ. และ คพ.","critical","doing","นายวิศวะ เก่งกาจ","ว่าจ้างบริษัทติดตั้ง CEMS และทดสอบระบบ","2026-06-30",None),
    ("LABOR-001","PG","ปรับปรุงนโยบายการลาตาม พ.ร.บ. คุ้มครองแรงงาน ฉบับที่ 9","ปรับปรุงระเบียบการลาคลอด ลาดูแลบุตร และลาประจำเดือนตามกฎหมายใหม่","high","todo",None,None,None,None),
    ("LABOR-002","PG","ปรับค่าแรงขั้นต่ำตามประกาศ พ.ศ. 2568","ตรวจสอบและปรับค่าแรงพนักงานทุกคนให้ไม่ต่ำกว่าค่าแรงขั้นต่ำใหม่","critical","done","นางสาวพิมพ์ใจ รักงาน",None,None,"2026-01-01"),
    ("QUALITY-001","QP","ต่ออายุการรับรอง มอก. สำหรับผลิตภัณฑ์เหล็ก","ดำเนินการต่ออายุใบรับรอง มอก. ทั้ง 22 ฉบับ และตรวจสอบ QR Code","critical","todo",None,None,None,None),
    ("TAX-003","AC","จัดทำเอกสาร Transfer Pricing ประจำปี","จัดทำเอกสาร Transfer Pricing สำหรับธุรกรรมกับบริษัทในเครือ","medium","doing","นายบัญชี ตรงไป","รวบรวมข้อมูลธุรกรรมและจัดทำรายงาน","2026-05-31",None),
    ("CSR-001","CSR","เตรียมความพร้อมสำหรับ HREDD - ทำแผนที่ห่วงโซ่อุปทาน","ดำเนินการทำแผนที่ห่วงโซ่อุปทานและประเมินความเสี่ยงด้านสิทธิมนุษยชน","high","todo",None,None,None,None),
]
for t in tasks:
    lid, did = law_id(t[0]), dept_id(t[1])
    if lid and did:
        conn.execute("INSERT OR IGNORE INTO compliance_tasks (law_id,department_id,title,description,priority,status,assignee,plan,due_date,completed_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (lid,did,t[2],t[3],t[4],t[5],t[6],t[7],t[8],t[9]))
conn.commit()
conn.close()
print("✅ Database seeded with real org structure")
