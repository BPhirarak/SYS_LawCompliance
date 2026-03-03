import { useState, useEffect } from 'react'
import { UserPlus, Trash2, Shield, User, KeyRound } from 'lucide-react'
import api from '../api'

export default function UserManagement({ auth }) {
  const [users, setUsers] = useState([])
  const [form, setForm] = useState({ username: '', password: '', role: 'user' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const headers = { 'x-role': auth.role }

  async function load() {
    try {
      const r = await api.get('/auth/users', { headers })
      setUsers(r.data)
    } catch (e) { setError(e.response?.data?.detail || 'โหลดข้อมูลไม่สำเร็จ') }
  }

  useEffect(() => { load() }, [])

  async function handleAdd(e) {
    e.preventDefault(); setError(''); setSuccess('')
    try {
      await api.post('/auth/users', form, { headers })
      setSuccess(`เพิ่มผู้ใช้ "${form.username}" สำเร็จ`)
      setForm({ username: '', password: '', role: 'user' })
      load()
    } catch (e) { setError(e.response?.data?.detail || 'เกิดข้อผิดพลาด') }
  }

  async function handleDelete(id, username) {
    if (!confirm(`ลบผู้ใช้ "${username}" ใช่หรือไม่?`)) return
    await api.delete(`/auth/users/${id}`, { headers })
    load()
  }

  async function handleReset(id, username) {
    if (!confirm(`Reset รหัสผ่านของ "${username}" เป็น "9999" ใช่หรือไม่?`)) return
    try {
      await api.post(`/auth/users/${id}/reset-password`, {}, { headers })
      setSuccess(`Reset รหัสผ่านของ "${username}" เป็น "9999" สำเร็จ`)
    } catch (e) { setError(e.response?.data?.detail || 'เกิดข้อผิดพลาด') }
  }

  return (
    <div className="p-6 max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">จัดการผู้ใช้งาน</h1>
        <p className="text-sm text-gray-500">เฉพาะ Admin เท่านั้น</p>
      </div>

      {/* Add user form */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-semibold text-gray-700 mb-4 flex items-center gap-2"><UserPlus size={16} /> เพิ่มผู้ใช้ใหม่</h2>
        <form onSubmit={handleAdd} className="flex gap-3 flex-wrap">
          <input value={form.username} onChange={e => setForm(f => ({...f, username: e.target.value}))}
            placeholder="ชื่อผู้ใช้" required
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1 min-w-32" />
          <input type="password" value={form.password} onChange={e => setForm(f => ({...f, password: e.target.value}))}
            placeholder="รหัสผ่าน" required
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1 min-w-32" />
          <select value={form.role} onChange={e => setForm(f => ({...f, role: e.target.value}))}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 text-sm font-medium">เพิ่ม</button>
        </form>
        {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
        {success && <p className="text-green-600 text-xs mt-2">{success}</p>}
      </div>

      {/* User list */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">ชื่อผู้ใช้</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">สิทธิ์</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">วันที่สร้าง</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">จัดการ</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-800">{u.username}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'}`}>
                    {u.role === 'admin' ? <Shield size={10} /> : <User size={10} />} {u.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500 text-xs">{u.created_at?.slice(0,10)}</td>
                <td className="px-4 py-3 text-right flex items-center justify-end gap-2">
                  {u.username !== 'admin1' && (
                    <>
                      <button onClick={() => handleReset(u.id, u.username)}
                        title="Reset รหัสผ่านเป็น 9999"
                        className="text-yellow-500 hover:text-yellow-700 p-1 rounded transition-colors">
                        <KeyRound size={14} />
                      </button>
                      <button onClick={() => handleDelete(u.id, u.username)}
                        title="ลบผู้ใช้"
                        className="text-red-400 hover:text-red-600 p-1 rounded transition-colors">
                        <Trash2 size={14} />
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
