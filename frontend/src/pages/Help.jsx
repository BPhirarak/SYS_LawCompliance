import { BookOpen, MessageSquare, Grid3X3, KanbanSquare, Users, Bot, Settings } from 'lucide-react'

export default function Help() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">คู่มือการใช้งานระบบ</h1>
        <p className="text-gray-600">Thai Law Compliance Management System for SYS Steel</p>
      </div>

      {/* Overview */}
      <section className="mb-8 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <BookOpen size={20} className="text-blue-600"/>
          ภาพรวมระบบ
        </h2>
        <p className="text-gray-700 leading-relaxed mb-4">
          ระบบจัดการความสอดคล้องกฎหมายสำหรับโรงงานอุตสาหกรรมเหล็ก ช่วยติดตามและจัดการกฎหมายที่เกี่ยวข้องกับการดำเนินงาน
          ครอบคลุม 9 หมวดหมู่กฎหมาย และ 25 หน่วยงานภายในองค์กร
        </p>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <p className="font-medium text-blue-900">กฎหมายในระบบ</p>
            <p className="text-2xl font-bold text-blue-600">17+ รายการ</p>
          </div>
          <div className="bg-green-50 rounded-lg p-3 border border-green-200">
            <p className="font-medium text-green-900">หน่วยงาน</p>
            <p className="text-2xl font-bold text-green-600">25 หน่วยงาน</p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="space-y-6">
        <h2 className="text-xl font-semibold text-gray-900">ฟีเจอร์หลัก</h2>

        {/* Dashboard */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Grid3X3 size={18} className="text-purple-600"/>
            Dashboard
          </h3>
          <p className="text-gray-700 text-sm leading-relaxed">
            แสดงภาพรวมสถานะ compliance ทั้งหมด สรุปจำนวน tasks แยกตามสถานะ (Todo/In Progress/Done)
            และระดับความสำคัญ พร้อมกราฟแสดงการกระจายตามหน่วยงานและหมวดหมู่กฎหมาย
          </p>
        </div>

        {/* Laws */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <BookOpen size={18} className="text-blue-600"/>
            กฏหมาย
          </h3>
          <ul className="text-gray-700 text-sm space-y-2 leading-relaxed">
            <li>• ดูรายการกฎหมายทั้งหมด กรองตามหมวดหมู่และระดับความเสี่ยง</li>
            <li>• คลิกดูรายละเอียดกฎหมาย บทลงโทษ และหน่วยงานที่เกี่ยวข้อง</li>
            <li>• กดปุ่ม "อ่านกฏหมายฉบับเต็ม" เพื่อเปิด URL ไปยังเว็บไซต์ราชกิจจานุเบกษา</li>
          </ul>
        </div>

        {/* Matrix */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Grid3X3 size={18} className="text-yellow-600"/>
            Matrix
          </h3>
          <ul className="text-gray-700 text-sm space-y-2 leading-relaxed">
            <li>• แสดงความสัมพันธ์ระหว่างหน่วยงานกับกฎหมาย</li>
            <li>• กรองตามหมวดหมู่กฎหมาย hover ที่ชื่อกฎหมายเพื่อดูรายละเอียด</li>
            <li>• สีแสดงระดับความเกี่ยวข้อง: แดง (Primary), ส้ม (High), เหลือง (Medium)</li>
          </ul>
        </div>

        {/* Kanban */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <KanbanSquare size={18} className="text-green-600"/>
            Compliance Kanban
          </h3>
          <ul className="text-gray-700 text-sm space-y-2 leading-relaxed">
            <li>• จัดการ tasks ด้วย Kanban board (Todo → In Progress → Done)</li>
            <li>• Drag & drop เพื่อเปลี่ยนสถานะ</li>
            <li>• คลิกที่ task เพื่อแก้ไขรายละเอียด กำหนดผู้รับผิดชอบ และวันครบกำหนด</li>
            <li>• กรองตามหน่วยงาน กฎหมาย และระดับความสำคัญ</li>
          </ul>
        </div>

        {/* Thoth Agent */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Bot size={18} className="text-cyan-600"/>
            Thoth-Legal Agent (AI Chatbot)
          </h3>
          <ul className="text-gray-700 text-sm space-y-2 leading-relaxed">
            <li>• ถามคำถามเกี่ยวกับกฎหมาย ผลกระทบต่อหน่วยงาน หรือ compliance tasks</li>
            <li>• พิมพ์ "อัปเดตกฏหมาย" เพื่อค้นหาการเปลี่ยนแปลงล่าสุด</li>
            <li>• Agent สามารถ query ข้อมูลจาก database ได้โดยตรง (tool calling)</li>
            <li>• กดปุ่ม ⚙️ เพื่อเปลี่ยน LLM provider/model (Anthropic, OpenAI, Bedrock, etc.)</li>
            <li>• กดปุ่ม 🕒 เพื่อดูประวัติการสนทนา</li>
            <li>• กดปุ่ม "หยุด" สีแดงเพื่อยกเลิกการประมวลผลกลางทาง</li>
          </ul>
        </div>

        {/* User Management */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Users size={18} className="text-purple-600"/>
            จัดการ User (Admin เท่านั้น)
          </h3>
          <ul className="text-gray-700 text-sm space-y-2 leading-relaxed">
            <li>• เพิ่ม/ลบ user accounts (role: user หรือ admin)</li>
            <li>• Reset รหัสผ่านเป็น "9999"</li>
            <li>• User ทุกคนสามารถเปลี่ยนรหัสผ่านของตนเองได้ผ่านไอคอนโปรไฟล์มุมขวาบน</li>
          </ul>
        </div>
      </section>

      {/* Quick Start */}
      <section className="mt-8 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border border-blue-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Settings size={20} className="text-blue-600"/>
          เริ่มต้นใช้งาน
        </h2>
        <ol className="text-gray-700 text-sm space-y-2 leading-relaxed list-decimal list-inside">
          <li>Login ด้วย username/password (default admin: admin1 / adm1219)</li>
          <li>ดูภาพรวมที่ Dashboard</li>
          <li>เข้าเมนู "กฏหมาย" เพื่อดูรายการกฎหมายทั้งหมด</li>
          <li>เข้า "Matrix" เพื่อดูความสัมพันธ์กฎหมาย↔หน่วยงาน</li>
          <li>เข้า "Compliance Kanban" เพื่อจัดการ tasks</li>
          <li>เปิด Thoth-Legal Agent (ปุ่มล่างขวา) เพื่อถามคำถาม</li>
        </ol>
      </section>

      {/* Support */}
      <section className="mt-8 bg-gray-50 rounded-xl border border-gray-200 p-6 text-center">
        <p className="text-gray-600 text-sm">
          ต้องการความช่วยเหลือเพิ่มเติม? ติดต่อ IT Support หรือดู Technical Documentation
        </p>
      </section>
    </div>
  )
}
