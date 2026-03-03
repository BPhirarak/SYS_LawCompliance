# Thai Law & Regulation Compliance Management

ระบบจัดการกฏหมายและข้อบังคับสำหรับโรงงานอุตสาหกรรมเหล็ก

## Tech Stack
- **Backend**: Python FastAPI + SQLite (built-in, ไม่ต้องติดตั้งเพิ่ม)
- **Frontend**: React + Vite + TailwindCSS + Recharts
- **Agent**: Python script สำหรับ monthly law scan

## การติดตั้งและรัน

### วิธีที่ 1: ใช้ start.bat (แนะนำ)
```
double-click start.bat
```

### วิธีที่ 2: รันแยก
```bash
# Backend
cd backend
pip install -r requirements.txt
python seed.py          # ครั้งแรกเท่านั้น
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## URL
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Features
- **Dashboard**: ภาพรวม compliance progress ทั้งบริษัท/ตามหน่วยงาน
- **กฏหมาย**: รายการกฏหมาย 15 ฉบับ ครอบคลุม 8 หมวด พร้อม filter และ risk level
- **Matrix**: ตาราง Department × Law แสดงความเกี่ยวข้อง แก้ไขได้
- **Kanban**: To Do → Doing → Done พร้อม filter ตามหน่วยงาน

## Monthly Agent
```bash
cd agent
python law_scanner.py
```
ใส่ OpenAI/Anthropic API key ใน environment เพื่อใช้งานจริง
