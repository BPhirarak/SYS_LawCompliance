import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { AlertTriangle, CheckCircle2, Clock, ListTodo, TrendingUp, Bell } from 'lucide-react'
import api from '../api'

const RISK_COLOR = { critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e' }
const STATUS_COLOR = { todo: '#94a3b8', doing: '#3b82f6', done: '#22c55e' }

function StatCard({ icon: Icon, label, value, color = 'blue', sub }) {
  const colors = { blue: 'bg-blue-50 text-blue-600', red: 'bg-red-50 text-red-600', green: 'bg-green-50 text-green-600', orange: 'bg-orange-50 text-orange-600', slate: 'bg-slate-50 text-slate-600' }
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-500">{label}</span>
        <div className={`p-2 rounded-lg ${colors[color]}`}><Icon size={18} /></div>
      </div>
      <div className="text-3xl font-bold text-gray-800">{value ?? '–'}</div>
      {sub && <div className="text-xs text-gray-400 mt-1">{sub}</div>}
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [deptFilter, setDeptFilter] = useState('')
  const [depts, setDepts] = useState([])

  useEffect(() => { api.get('/departments').then(r => setDepts(r.data)) }, [])
  useEffect(() => {
    api.get('/dashboard', { params: deptFilter ? { department_id: deptFilter } : {} })
      .then(r => setData(r.data))
  }, [deptFilter])

  if (!data) return <div className="p-8 text-gray-400">กำลังโหลด...</div>
  const { summary, byDept, byCategory, recentUpdates, lawStats } = data

  const pieData = [
    { name: 'To Do', value: summary.todo || 0, color: STATUS_COLOR.todo },
    { name: 'Doing', value: summary.doing || 0, color: STATUS_COLOR.doing },
    { name: 'Done', value: summary.done || 0, color: STATUS_COLOR.done },
  ]

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-sm text-gray-500">ภาพรวม Compliance ทั้งบริษัท</p>
        </div>
        <select value={deptFilter} onChange={e => setDeptFilter(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm bg-white shadow-sm">
          <option value="">ทั้งบริษัท</option>
          {depts.map(d => <option key={d.id} value={d.id}>{d.name_th}</option>)}
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={ListTodo} label="งานทั้งหมด" value={summary.total} color="slate" />
        <StatCard icon={Clock} label="กำลังดำเนินการ" value={summary.doing} color="blue" />
        <StatCard icon={AlertTriangle} label="Critical ที่ยังค้าง" value={summary.critical_open} color="red" />
        <StatCard icon={CheckCircle2} label="เสร็จแล้ว" value={summary.done} color="green" sub={`${summary.total ? Math.round((summary.done / summary.total) * 100) : 0}% ของทั้งหมด`} />
      </div>

      {summary.overdue > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
          <AlertTriangle size={20} className="text-red-500 shrink-0" />
          <span className="text-red-700 text-sm font-medium">มีงาน <strong>{summary.overdue} รายการ</strong> ที่เกินกำหนดและยังไม่เสร็จ</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Progress by Dept */}
        <div className="lg:col-span-2 bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-700 mb-4">ความคืบหน้าตามหน่วยงาน</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={byDept} layout="vertical" margin={{ left: 10 }}>
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name_th" width={160} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="done" name="Done" stackId="a" fill={STATUS_COLOR.done} />
              <Bar dataKey="doing" name="Doing" stackId="a" fill={STATUS_COLOR.doing} />
              <Bar dataKey="todo" name="To Do" stackId="a" fill={STATUS_COLOR.todo} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-700 mb-4">สัดส่วนสถานะงาน</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Category */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-700 mb-4">ความคืบหน้าตามหมวดกฏหมาย</h2>
          <div className="space-y-3">
            {byCategory.filter(c => (c.todo || 0) + (c.doing || 0) + (c.done || 0) > 0).map(c => {
              const total = (c.todo || 0) + (c.doing || 0) + (c.done || 0)
              const pct = total ? Math.round(((c.done || 0) / total) * 100) : 0
              return (
                <div key={c.code}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{c.category}</span>
                    <span className="text-gray-400">{c.done || 0}/{total}</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Recent Updates */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Bell size={16} /> การอัปเดตกฏหมายล่าสุด
          </h2>
          {recentUpdates.length === 0
            ? <p className="text-sm text-gray-400">ยังไม่มีการอัปเดต</p>
            : recentUpdates.map(u => (
              <div key={u.id} className="border-l-4 border-blue-400 pl-3 py-2 mb-3">
                <p className="text-sm font-medium text-gray-700">{u.law_name}</p>
                <p className="text-xs text-gray-500">{u.summary}</p>
                <p className="text-xs text-gray-400 mt-1">{u.detected_at?.slice(0, 10)}</p>
              </div>
            ))
          }
        </div>
      </div>
    </div>
  )
}
