import { useEffect, useState } from 'react'
import api from '../api'

const LEVEL_STYLE = {
  primary: 'bg-blue-600 text-white font-bold',
  high: 'bg-blue-200 text-blue-800',
  medium: 'bg-slate-200 text-slate-700',
  low: 'bg-gray-100 text-gray-400',
  '': 'bg-white text-gray-200',
}
const LEVEL_LABEL = { primary: '★★', high: '★', medium: '◆', low: '·', '': '' }

const RISK_DOT = { critical: 'bg-red-500', high: 'bg-orange-400', medium: 'bg-yellow-400', low: 'bg-green-400' }

export default function LawMatrix() {
  const [data, setData] = useState(null)
  const [categories, setCategories] = useState([])
  const [catFilter, setCatFilter] = useState('')
  const [editing, setEditing] = useState(null)
  const [tooltip, setTooltip] = useState(null) // { law, x, y }

  useEffect(() => {
    api.get('/departments/meta/matrix').then(r => setData(r.data))
    api.get('/laws/meta/categories').then(r => setCategories(r.data))
  }, [])

  const handleCellClick = (dept_id, law_id, current) => {
    setEditing({ dept_id, law_id, current: current || '' })
  }

  const saveEdit = async (level) => {
    await api.put('/departments/meta/matrix', { department_id: editing.dept_id, law_id: editing.law_id, relevance_level: level })
    const r = await api.get('/departments/meta/matrix')
    setData(r.data)
    setEditing(null)
  }

  if (!data) return <div className="p-8 text-gray-400">กำลังโหลด...</div>

  const filteredLaws = catFilter ? data.laws.filter(l => l.category_code === catFilter) : data.laws

  return (
    <div className="p-6 flex flex-col gap-5 h-screen overflow-hidden">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Department × Law Matrix</h1>
        <p className="text-sm text-gray-500">แสดงความเกี่ยวข้องของแต่ละหน่วยงานกับกฏหมาย · คลิก cell เพื่อแก้ไข</p>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-xs shrink-0">
        {Object.entries(LEVEL_LABEL).filter(([k]) => k).map(([k, v]) => (
          <span key={k} className={`px-2 py-1 rounded border ${LEVEL_STYLE[k]}`}>{v} {k}</span>
        ))}
        <span className="px-2 py-1 rounded border bg-white text-gray-300">– ไม่เกี่ยวข้อง</span>
      </div>

      {/* Category filter */}
      <div className="flex gap-2 flex-wrap shrink-0">
        <button onClick={() => setCatFilter('')} className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${!catFilter ? 'bg-slate-800 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}>ทั้งหมด</button>
        {categories.map(c => (
          <button key={c.code} onClick={() => setCatFilter(c.code)}
            className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${catFilter === c.code ? 'bg-slate-800 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}>
            {c.code}
          </button>
        ))}
      </div>

      {/* Matrix Table - scrollable both directions */}
      <div className="flex-1 overflow-auto rounded-xl border border-gray-200 shadow-sm bg-white min-h-0">
        <table className="text-xs border-collapse" style={{ minWidth: 'max-content' }}>
          <thead className="sticky top-0 z-20">
            <tr className="bg-slate-800 text-white">
              <th className="sticky left-0 z-10 bg-slate-800 px-4 py-3 text-left font-medium min-w-48">หน่วยงาน</th>
              {filteredLaws.map(l => (
                <th key={l.id} className="px-2 py-3 text-center font-normal max-w-24 min-w-20">
                  <div className="flex flex-col items-center gap-1">
                    <span className={`w-2 h-2 rounded-full ${RISK_DOT[l.risk_level]}`} title={l.risk_level} />
                    <span className="text-slate-300 font-mono">{l.code}</span>
                  </div>
                </th>
              ))}
            </tr>
            <tr className="bg-slate-700 text-slate-300">
              <th className="sticky left-0 z-10 bg-slate-700 px-4 py-2" />
              {filteredLaws.map(l => (
                <th key={l.id} className="px-2 py-2 text-center max-w-24"
                  onMouseEnter={e => {
                    const rect = e.currentTarget.getBoundingClientRect()
                    setTooltip({ law: l, x: rect.left + rect.width / 2, y: rect.bottom + 6 })
                  }}
                  onMouseLeave={() => setTooltip(null)}>
                  <div className="text-xs leading-tight font-normal cursor-default select-none">
                    {l.name_th.slice(0, 30)}{l.name_th.length > 30 ? '…' : ''}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.departments.map((dept, di) => (
              <tr key={dept.id} className={di % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className={`sticky left-0 z-10 px-4 py-3 font-medium text-gray-700 border-r border-gray-200 ${di % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                  {dept.name_th}
                </td>
                {filteredLaws.map(law => {
                  const level = data.matrix[String(dept.id)]?.[String(law.id)] || ''
                  return (
                    <td key={law.id} className="px-1 py-2 text-center border-r border-gray-100 last:border-0">
                      <button onClick={() => handleCellClick(dept.id, law.id, level)}
                        className={`w-10 h-8 rounded text-xs transition-all hover:opacity-80 hover:scale-110 ${LEVEL_STYLE[level] || LEVEL_STYLE['']}`}
                        title={`${dept.name_th} × ${law.code}: ${level || 'ไม่เกี่ยวข้อง'}`}>
                        {LEVEL_LABEL[level] || ''}
                      </button>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Tooltip - fixed position to escape overflow clipping */}
      {tooltip && (
        <div className="fixed z-[9999] pointer-events-none"
          style={{ left: tooltip.x, top: tooltip.y, transform: 'translateX(-50%)' }}>
          <div className="w-64 bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-xl">
            <p className="font-semibold text-blue-300 mb-1">{tooltip.law.code}</p>
            <p className="leading-relaxed">{tooltip.law.name_th}</p>
            {tooltip.law.category_name && <p className="mt-1 text-gray-400">{tooltip.law.category_name}</p>}
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={() => setEditing(null)}>
          <div className="bg-white rounded-2xl p-6 shadow-2xl w-72" onClick={e => e.stopPropagation()}>
            <h3 className="font-semibold text-gray-800 mb-4">กำหนดระดับความเกี่ยวข้อง</h3>
            <div className="space-y-2">
              {['primary', 'high', 'medium', 'low', ''].map(level => (
                <button key={level} onClick={() => saveEdit(level || 'none')}
                  className={`w-full px-4 py-2.5 rounded-lg text-sm text-left border transition-colors hover:opacity-80 ${editing.current === level ? 'ring-2 ring-blue-400' : ''} ${LEVEL_STYLE[level] || 'bg-white text-gray-500'}`}>
                  {level ? `${LEVEL_LABEL[level]} ${level}` : '– ไม่เกี่ยวข้อง'}
                </button>
              ))}
            </div>
            <button onClick={() => setEditing(null)} className="mt-4 w-full text-sm text-gray-400 hover:text-gray-600">ยกเลิก</button>
          </div>
        </div>
      )}
    </div>
  )
}
