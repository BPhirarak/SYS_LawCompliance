import { useEffect, useState } from 'react'
import { Search, ChevronDown, ChevronUp, ExternalLink, AlertTriangle } from 'lucide-react'
import api from '../api'

const RISK_BADGE = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high: 'bg-orange-100 text-orange-700 border-orange-200',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  low: 'bg-green-100 text-green-700 border-green-200',
}
const RISK_LABEL = { critical: 'วิกฤต', high: 'สูง', medium: 'ปานกลาง', low: 'ต่ำ' }

function LawCard({ law }) {
  const [open, setOpen] = useState(false)
  const [detail, setDetail] = useState(null)

  const loadDetail = async () => {
    if (!open && !detail) {
      const r = await api.get(`/laws/${law.id}`)
      setDetail(r.data)
    }
    setOpen(!open)
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <button onClick={loadDetail} className="w-full text-left p-4 hover:bg-gray-50 transition-colors">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-xs font-mono text-gray-400">{law.code}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${RISK_BADGE[law.risk_level]}`}>
                {RISK_LABEL[law.risk_level]}
              </span>
              <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{law.category_name}</span>
            </div>
            <p className="font-medium text-gray-800 text-sm leading-snug">{law.name_th}</p>
            {law.description && <p className="text-xs text-gray-500 mt-1 line-clamp-2">{law.description}</p>}
          </div>
          {open ? <ChevronUp size={16} className="text-gray-400 shrink-0 mt-1" /> : <ChevronDown size={16} className="text-gray-400 shrink-0 mt-1" />}
        </div>
      </button>

      {open && detail && (
        <div className="border-t border-gray-100 p-4 bg-gray-50 space-y-3">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="text-gray-400 text-xs">วันที่มีผลบังคับใช้</span><p className="font-medium">{detail.effective_date || '–'}</p></div>
            <div><span className="text-gray-400 text-xs">สถานะ</span><p className="font-medium capitalize">{detail.status}</p></div>
          </div>
          {detail.penalty_summary && (
            <div className="bg-red-50 border border-red-100 rounded-lg p-3">
              <p className="text-xs text-red-600 font-medium flex items-center gap-1"><AlertTriangle size={12} /> บทลงโทษ</p>
              <p className="text-sm text-red-700 mt-1">{detail.penalty_summary}</p>
            </div>
          )}
          {detail.departments?.length > 0 && (
            <div>
              <p className="text-xs text-gray-400 mb-2">หน่วยงานที่เกี่ยวข้อง</p>
              <div className="flex flex-wrap gap-2">
                {detail.departments.map(d => (
                  <span key={d.id} className={`text-xs px-2 py-1 rounded-full border ${d.relevance_level === 'primary' ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-gray-100 border-gray-200 text-gray-600'}`}>
                    {d.name_th} {d.relevance_level === 'primary' ? '★' : ''}
                  </span>
                ))}
              </div>
            </div>
          )}
          {detail.updates?.length > 0 && (
            <div>
              <p className="text-xs text-gray-400 mb-2">ประวัติการอัปเดต</p>
              {detail.updates.map(u => (
                <div key={u.id} className="text-xs border-l-2 border-blue-300 pl-2 mb-2">
                  <span className="font-medium text-blue-600">{u.update_type}</span> · {u.detected_at?.slice(0, 10)}
                  <p className="text-gray-600">{u.summary}</p>
                </div>
              ))}
            </div>
          )}
          {/* Source URL */}
          {detail.source_url && (
            <a href={detail.source_url} target="_blank" rel="noopener noreferrer"
              onClick={e => e.stopPropagation()}
              className="inline-flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg px-3 py-1.5 transition-colors font-medium">
              <ExternalLink size={12} />
              อ่านกฏหมายฉบับเต็ม
            </a>
          )}
        </div>
      )}
    </div>
  )
}

export default function LawList() {
  const [laws, setLaws] = useState([])
  const [categories, setCategories] = useState([])
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState('')
  const [riskFilter, setRiskFilter] = useState('')

  const load = () => {
    api.get('/laws', { params: { search: search || undefined, category: catFilter || undefined, risk_level: riskFilter || undefined } })
      .then(r => setLaws(r.data))
  }

  useEffect(() => { api.get('/laws/meta/categories').then(r => setCategories(r.data)) }, [])
  useEffect(() => { load() }, [search, catFilter, riskFilter])

  return (
    <div className="p-6 space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">กฏหมายและข้อบังคับ</h1>
        <p className="text-sm text-gray-500">ครอบคลุม 11 ด้าน อัปเดต พ.ศ. 2568</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="ค้นหากฏหมาย..."
            className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
        </div>
        <select value={catFilter} onChange={e => setCatFilter(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm bg-white shadow-sm">
          <option value="">ทุกหมวด</option>
          {categories.map(c => <option key={c.code} value={c.code}>{c.name_th}</option>)}
        </select>
        <select value={riskFilter} onChange={e => setRiskFilter(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm bg-white shadow-sm">
          <option value="">ทุกระดับความเสี่ยง</option>
          <option value="critical">วิกฤต</option>
          <option value="high">สูง</option>
          <option value="medium">ปานกลาง</option>
          <option value="low">ต่ำ</option>
        </select>
      </div>

      <p className="text-sm text-gray-400">{laws.length} รายการ</p>

      <div className="space-y-3">
        {laws.map(l => <LawCard key={l.id} law={l} />)}
      </div>
    </div>
  )
}
