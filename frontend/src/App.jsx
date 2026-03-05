import { useState } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import { LayoutDashboard, Scale, Grid3X3, KanbanSquare, Users, LogOut, UserCircle, X, HelpCircle } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import LawList from './pages/LawList'
import LawMatrix from './pages/LawMatrix'
import Kanban from './pages/Kanban'
import Login from './pages/Login'
import UserManagement from './pages/UserManagement'
import Help from './pages/Help'
import ChatBot from './components/ChatBot'
import api from './api'

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/laws', icon: Scale, label: 'กฏหมาย' },
  { to: '/matrix', icon: Grid3X3, label: 'Matrix' },
  { to: '/kanban', icon: KanbanSquare, label: 'Compliance Kanban' },
  { to: '/help', icon: HelpCircle, label: 'Help' },
]

function ChangePasswordModal({ auth, onClose }) {
  const [form, setForm] = useState({ old_password: '', new_password: '', confirm: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function handleSubmit(e) {
    e.preventDefault(); setError(''); setSuccess('')
    if (form.new_password !== form.confirm) { setError('รหัสผ่านใหม่ไม่ตรงกัน'); return }
    if (form.new_password.length < 4) { setError('รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร'); return }
    try {
      await api.post('/auth/change-password', {
        username: auth.username,
        old_password: form.old_password,
        new_password: form.new_password
      })
      setSuccess('เปลี่ยนรหัสผ่านสำเร็จ')
      setForm({ old_password: '', new_password: '', confirm: '' })
    } catch (e) { setError(e.response?.data?.detail || 'เกิดข้อผิดพลาด') }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl p-6 shadow-2xl w-80" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-800">เปลี่ยนรหัสผ่าน</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={18} /></button>
        </div>
        <p className="text-xs text-gray-500 mb-4">ผู้ใช้: <span className="font-medium text-gray-700">{auth.username}</span></p>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input type="password" placeholder="รหัสผ่านเดิม" required value={form.old_password}
            onChange={e => setForm(f => ({...f, old_password: e.target.value}))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <input type="password" placeholder="รหัสผ่านใหม่" required value={form.new_password}
            onChange={e => setForm(f => ({...f, new_password: e.target.value}))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <input type="password" placeholder="ยืนยันรหัสผ่านใหม่" required value={form.confirm}
            onChange={e => setForm(f => ({...f, confirm: e.target.value}))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {error && <p className="text-red-500 text-xs">{error}</p>}
          {success && <p className="text-green-600 text-xs">{success}</p>}
          <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 text-sm font-medium">
            บันทึก
          </button>
        </form>
      </div>
    </div>
  )
}

export default function App() {
  const [auth, setAuth] = useState(() => {
    try { return JSON.parse(localStorage.getItem('auth')) } catch { return null }
  })
  const [showChangePw, setShowChangePw] = useState(false)

  function handleLogin(data) { localStorage.setItem('auth', JSON.stringify(data)); setAuth(data) }
  function handleLogout() { localStorage.removeItem('auth'); setAuth(null) }

  if (!auth) return <Login onLogin={handleLogin} />

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col shrink-0">
        <div className="p-5 border-b border-slate-700">
          <div className="flex items-center gap-2 mb-1">
            <Scale size={22} className="text-blue-400" />
            <span className="font-bold text-lg leading-tight">Thai Law</span>
          </div>
          <p className="text-xs text-slate-400">Compliance Management</p>
          <p className="text-xs text-slate-500 mt-1">โรงงานอุตสาหกรรมเหล็ก</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`
              }>
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
          {/* Admin only */}
          {auth.role === 'admin' && (
            <NavLink to="/users"
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-purple-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`
              }>
              <Users size={18} />
              จัดการ User
            </NavLink>
          )}
        </nav>
        {/* User info + logout */}
        <div className="p-4 border-t border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-300 font-medium">{auth.username}</p>
              <p className="text-xs text-slate-500">{auth.role}</p>
            </div>
            <button onClick={handleLogout} title="ออกจากระบบ"
              className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-700 transition-colors">
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto relative">
        {/* Profile icon top-right */}
        <div className="absolute top-4 right-4 z-30">
          <button onClick={() => setShowChangePw(true)}
            title="เปลี่ยนรหัสผ่าน"
            className="flex items-center gap-2 bg-white border border-gray-200 rounded-full px-3 py-1.5 shadow-sm hover:shadow-md transition-shadow text-sm text-gray-600 hover:text-gray-800">
            <UserCircle size={18} className="text-blue-500" />
            <span className="text-xs font-medium">{auth.username}</span>
          </button>
        </div>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/laws" element={<LawList />} />
          <Route path="/matrix" element={<LawMatrix />} />
          <Route path="/kanban" element={<Kanban />} />
          <Route path="/help" element={<Help />} />
          {auth.role === 'admin' && <Route path="/users" element={<UserManagement auth={auth} />} />}
        </Routes>
      </main>

      <ChatBot auth={auth} />

      {showChangePw && <ChangePasswordModal auth={auth} onClose={() => setShowChangePw(false)} />}
    </div>
  )
}
