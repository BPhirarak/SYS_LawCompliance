import { useEffect, useState } from 'react'
import { Plus, X, ChevronRight, AlertTriangle, Calendar, User } from 'lucide-react'
import api from '../api'

const COLUMNS = [
  { key: 'todo', label: 'To Do', color: 'bg-slate-100 border-slate-300', headerColor: 'bg-slate-600' },
  { key: 'doing', label: 'Doing', color: 'bg-blue-50 border-blue-200', headerColor: 'bg-blue-600' },
  { key: 'done', label: 'Done', color: 'bg-green-50 border-green-200', headerColor: 'bg-green-600' },
]

const PRIORITY_BADGE = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-500',
}

function TaskCard({ task, onMove, onEdit }) {
  const isOverdue = task.due_date && task.status !== 'done' && new Date(task.due_date) < new Date()
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 space-y-2 hover:shadow-md transition-shadow cursor-pointer" onClick={() => onEdit(task)}>
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-medium text-gray-800 leading-snug flex-1">{task.title}</p>
        <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${PRIORITY_BADGE[task.priority]}`}>{task.priority}</span>
      </div>
      {task.law_name && <p className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">{task.law_code} · {task.law_name?.slice(0, 40)}{task.law_name?.length > 40 ? '…' : ''}</p>}
      {task.dept_name && <p className="text-xs text-gray-500">{task.dept_name}</p>}
      {task.assignee && <p className="text-xs text-gray-500 flex items-center gap-1"><User size={11} />{task.assignee}</p>}
      {task.due_date && (
        <p className={`text-xs flex items-center gap-1 ${isOverdue ? 'text-red-500 font-medium' : 'text-gray-400'}`}>
          <Calendar size={11} />{task.due_date} {isOverdue && '⚠ เกินกำหนด'}
        </p>
      )}
      {/* Move buttons */}
      <div className="flex gap-1 pt-1" onClick={e => e.stopPropagation()}>
        {task.status !== 'todo' && <button onClick={() => onMove(task.id, task.status === 'doing' ? 'todo' : 'doing')} className="text-xs px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-600">← ย้อนกลับ</button>}
        {task.status !== 'done' && <button onClick={() => onMove(task.id, task.status === 'todo' ? 'doing' : 'done')} className="text-xs px-2 py-1 rounded bg-blue-100 hover:bg-blue-200 text-blue-700 flex items-center gap-1">ถัดไป <ChevronRight size={12} /></button>}
      </div>
    </div>
  )
}

function TaskModal({ task, laws, depts, onClose, onSave }) {
  const [form, setForm] = useState(task || { law_id: '', department_id: '', title: '', description: '', priority: 'medium', assignee: '', plan: '', due_date: '' })
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSave = async () => {
    if (!form.title) return
    if (task?.id) {
      await api.put(`/tasks/${task.id}`, form)
    } else {
      await api.post('/tasks', form)
    }
    onSave()
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-5 border-b">
          <h3 className="font-semibold text-gray-800">{task?.id ? 'แก้ไข Task' : 'สร้าง Task ใหม่'}</h3>
          <button onClick={onClose}><X size={18} className="text-gray-400" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">ชื่องาน *</label>
            <input value={form.title} onChange={e => set('title', e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">รายละเอียด</label>
            <textarea value={form.description || ''} onChange={e => set('description', e.target.value)} rows={3} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-500 mb-1 block">กฏหมายที่เกี่ยวข้อง</label>
              <select value={form.law_id || ''} onChange={e => set('law_id', e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
                <option value="">เลือกกฏหมาย</option>
                {laws.map(l => <option key={l.id} value={l.id}>{l.code} · {l.name_th?.slice(0, 30)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">หน่วยงาน</label>
              <select value={form.department_id || ''} onChange={e => set('department_id', e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
                <option value="">เลือกหน่วยงาน</option>
                {depts.map(d => <option key={d.id} value={d.id}>{d.name_th}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Priority</label>
              <select value={form.priority} onChange={e => set('priority', e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">กำหนดเสร็จ</label>
              <input type="date" value={form.due_date || ''} onChange={e => set('due_date', e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">ผู้รับผิดชอบ</label>
            <input value={form.assignee || ''} onChange={e => set('assignee', e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">แผนงาน</label>
            <textarea value={form.plan || ''} onChange={e => set('plan', e.target.value)} rows={2} className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
          </div>
        </div>
        <div className="flex gap-3 p-5 border-t">
          <button onClick={handleSave} className="flex-1 bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700 transition-colors">บันทึก</button>
          <button onClick={onClose} className="px-4 py-2.5 border rounded-lg text-sm text-gray-600 hover:bg-gray-50">ยกเลิก</button>
        </div>
      </div>
    </div>
  )
}

export default function Kanban() {
  const [tasks, setTasks] = useState([])
  const [laws, setLaws] = useState([])
  const [depts, setDepts] = useState([])
  const [deptFilter, setDeptFilter] = useState('')
  const [modal, setModal] = useState(null) // null | task object | 'new'

  const load = () => {
    api.get('/tasks', { params: deptFilter ? { department_id: deptFilter } : {} }).then(r => setTasks(r.data))
  }

  useEffect(() => {
    api.get('/laws').then(r => setLaws(r.data))
    api.get('/departments').then(r => setDepts(r.data))
  }, [])

  useEffect(() => { load() }, [deptFilter])

  const moveTask = async (id, newStatus) => {
    await api.put(`/tasks/${id}`, { status: newStatus })
    load()
  }

  const handleSave = () => { setModal(null); load() }

  const grouped = { todo: [], doing: [], done: [] }
  tasks.forEach(t => { if (grouped[t.status]) grouped[t.status].push(t) })

  return (
    <div className="p-6 space-y-5 h-full">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Compliance Kanban</h1>
          <p className="text-sm text-gray-500">ติดตามแผนงาน Compliance ของแต่ละหน่วยงาน</p>
        </div>
        <div className="flex gap-3">
          <select value={deptFilter} onChange={e => setDeptFilter(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm bg-white shadow-sm">
            <option value="">ทุกหน่วยงาน</option>
            {depts.map(d => <option key={d.id} value={d.id}>{d.name_th}</option>)}
          </select>
          <button onClick={() => setModal({ law_id: '', department_id: '', title: '', priority: 'medium' })}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
            <Plus size={16} /> เพิ่ม Task
          </button>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {COLUMNS.map(col => (
          <div key={col.key} className={`rounded-xl border-2 ${col.color} flex flex-col min-h-96`}>
            <div className={`${col.headerColor} text-white px-4 py-3 rounded-t-xl flex items-center justify-between`}>
              <span className="font-semibold">{col.label}</span>
              <span className="bg-white/20 text-white text-xs px-2 py-0.5 rounded-full">{grouped[col.key].length}</span>
            </div>
            <div className="flex-1 p-3 space-y-3 overflow-y-auto">
              {grouped[col.key].length === 0
                ? <p className="text-xs text-gray-400 text-center py-8">ไม่มีงาน</p>
                : grouped[col.key].map(t => (
                  <TaskCard key={t.id} task={t} onMove={moveTask} onEdit={setModal} />
                ))
              }
            </div>
          </div>
        ))}
      </div>

      {modal && <TaskModal task={modal?.id ? modal : null} laws={laws} depts={depts} onClose={() => setModal(null)} onSave={handleSave} />}
    </div>
  )
}
