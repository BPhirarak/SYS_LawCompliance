import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Loader2, User, ChevronDown,
         PlusCircle, Trash2, RefreshCw } from 'lucide-react'

const ThothIcon = ({ size = 20, className = '' }) => (
  <img src="/thoth.png" alt="Thoth" width={size} height={size}
    className={`rounded-full object-cover ${className}`}
    onError={e => { e.target.style.display='none' }} />
)
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const API = 'http://localhost:8000'

const RISK_COLOR = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high:     'bg-orange-100 text-orange-700 border-orange-200',
  medium:   'bg-yellow-100 text-yellow-700 border-yellow-200',
  low:      'bg-green-100 text-green-700 border-green-200',
}
const RISK_LABEL = { critical: '🔴 Critical', high: '🟠 High', medium: '🟡 Medium', low: '🟢 Low' }

// ── Law Update Card ────────────────────────────────────────────────────────────
function LawUpdateCard({ update }) {
  const action = update.action
  if (action === 'add_law') return (
    <div className="mt-2 rounded-xl border border-green-200 bg-green-50 p-3 text-xs space-y-1.5">
      <div className="flex items-center gap-1.5 font-semibold text-green-700">
        <PlusCircle size={13} /> เพิ่มกฏหมายใหม่
      </div>
      <p className="font-bold text-gray-800">[{update.law_code}] {update.name_th}</p>
      {update.description && <p className="text-gray-600 leading-relaxed">{update.description}</p>}
      <div className="flex flex-wrap gap-1.5 pt-0.5">
        {update.risk_level && <span className={`px-2 py-0.5 rounded-full border text-xs ${RISK_COLOR[update.risk_level]}`}>{RISK_LABEL[update.risk_level]}</span>}
        {update.effective_date && <span className="px-2 py-0.5 rounded-full border bg-blue-50 text-blue-700 border-blue-200">มีผล {update.effective_date}</span>}
        {update.matrix_created > 0 && <span className="px-2 py-0.5 rounded-full border bg-slate-100 text-slate-600 border-slate-200">Matrix {update.matrix_created} หน่วยงาน</span>}
        {update.tasks_created > 0 && <span className="px-2 py-0.5 rounded-full border bg-purple-50 text-purple-700 border-purple-200">Tasks {update.tasks_created} รายการ</span>}
      </div>
      {update.penalty_summary && <p className="text-red-600 text-xs">⚠️ {update.penalty_summary}</p>}
      {update.added === false && <p className="text-amber-600">⚠️ กฏหมายนี้มีอยู่แล้วในระบบ</p>}
    </div>
  )

  if (action === 'update_law') return (
    <div className="mt-2 rounded-xl border border-blue-200 bg-blue-50 p-3 text-xs space-y-1.5">
      <div className="flex items-center gap-1.5 font-semibold text-blue-700">
        <RefreshCw size={13} /> อัปเดตกฏหมาย [{update.law_code}]
      </div>
      {update.summary && <p className="text-gray-700">{update.summary}</p>}
      {update.changes && (
        <div className="space-y-1">
          {update.changes.old && <p className="line-through text-gray-400">{update.changes.old}</p>}
          {update.changes.new && <p className="text-gray-800 font-medium">{update.changes.new}</p>}
        </div>
      )}
      {update.source && <p className="text-gray-400">📎 {update.source}</p>}
    </div>
  )

  if (action === 'remove_law') return (
    <div className="mt-2 rounded-xl border border-red-200 bg-red-50 p-3 text-xs space-y-1.5">
      <div className="flex items-center gap-1.5 font-semibold text-red-700">
        <Trash2 size={13} /> ลบกฏหมาย [{update.law_code}]
      </div>
      {update.law_name && <p className="text-gray-700">{update.law_name}</p>}
      {update.reason && <p className="text-gray-500">{update.reason}</p>}
      {update.removed === false && <p className="text-amber-600">⚠️ ไม่พบกฏหมายรหัสนี้ในระบบ</p>}
      {update.removed === true && <p className="text-red-600 font-medium">✓ ลบออกจากระบบแล้ว</p>}
    </div>
  )

  return null
}

// ── Markdown Message ───────────────────────────────────────────────────────────
function MarkdownMessage({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // Tables → styled
        table: ({ children }) => (
          <div className="overflow-x-auto my-2 rounded-lg border border-gray-200">
            <table className="text-xs w-full border-collapse">{children}</table>
          </div>
        ),
        thead: ({ children }) => <thead className="bg-slate-700 text-white">{children}</thead>,
        tbody: ({ children }) => <tbody className="divide-y divide-gray-100">{children}</tbody>,
        th: ({ children }) => <th className="px-3 py-2 text-left font-medium whitespace-nowrap">{children}</th>,
        td: ({ children }) => <td className="px-3 py-2 text-gray-700">{children}</td>,
        tr: ({ children }) => <tr className="hover:bg-gray-50">{children}</tr>,
        // Code blocks
        code: ({ inline, children }) => inline
          ? <code className="bg-gray-200 text-red-600 px-1 rounded text-xs font-mono">{children}</code>
          : <pre className="bg-gray-800 text-green-300 rounded-lg p-3 text-xs overflow-x-auto my-2 font-mono"><code>{children}</code></pre>,
        // Bold
        strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
        // Lists
        ul: ({ children }) => <ul className="list-disc list-inside space-y-0.5 my-1 text-gray-700">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside space-y-0.5 my-1 text-gray-700">{children}</ol>,
        li: ({ children }) => <li className="text-sm leading-relaxed">{children}</li>,
        // Paragraphs
        p: ({ children }) => <p className="text-sm leading-relaxed mb-1 last:mb-0">{children}</p>,
        // Headings
        h1: ({ children }) => <p className="font-bold text-base text-gray-900 mt-2 mb-1">{children}</p>,
        h2: ({ children }) => <p className="font-bold text-sm text-gray-800 mt-2 mb-1">{children}</p>,
        h3: ({ children }) => <p className="font-semibold text-sm text-gray-700 mt-1 mb-0.5">{children}</p>,
        // Blockquote → info box
        blockquote: ({ children }) => (
          <div className="border-l-4 border-blue-400 bg-blue-50 pl-3 py-1 my-1 rounded-r-lg text-blue-800 text-xs">{children}</div>
        ),
        // HR
        hr: () => <hr className="my-2 border-gray-200" />,
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

// ── Main ChatBot ───────────────────────────────────────────────────────────────
export default function ChatBot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'สวัสดีครับ ผมคือ **Thoth-Legal Agent** สำหรับ SYS Steel\n\nสามารถถามเกี่ยวกับ:\n- รายละเอียดกฏหมายในระบบ\n- ผลกระทบต่อหน่วยงาน\n- พิมพ์ **"อัปเดตกฏหมาย"** เพื่อค้นหาการเปลี่ยนแปลงล่าสุด', updates: [] }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [totalUpdates, setTotalUpdates] = useState(0)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  async function send() {
    const msg = input.trim()
    if (!msg || loading) return
    setInput('')
    const history = messages.filter(m => m.role !== 'system').slice(-10).map(m => ({ role: m.role, content: m.content }))
    setMessages(prev => [...prev, { role: 'user', content: msg, updates: [] }])
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, session_id: sessionId, history })
      })
      const data = await res.json()
      setSessionId(data.session_id)
      const cleanReply = data.reply.replace(/<law_update>[\s\S]*?<\/law_update>/g, '').trim()
      const updates = data.law_updates || []
      setMessages(prev => [...prev, { role: 'assistant', content: cleanReply, updates }])
      if (updates.length > 0) setTotalUpdates(n => n + updates.length)
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ ไม่สามารถเชื่อมต่อกับ server ได้ กรุณาตรวจสอบว่า backend กำลังทำงานอยู่', updates: [] }])
    }
    setLoading(false)
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  return (
    <>
      {/* Floating button */}
      <button onClick={() => { setOpen(o => !o); setTotalUpdates(0) }}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-slate-900 hover:bg-slate-800 text-white rounded-full shadow-lg flex items-center justify-center transition-all overflow-hidden border-2 border-cyan-400"
        title="Thoth-Legal Agent">
        {open ? <X size={22} /> : <ThothIcon size={48} />}
        {!open && totalUpdates > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
            {totalUpdates}
          </span>
        )}
      </button>

      {/* Chat window */}
      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-[420px] max-h-[640px] bg-white rounded-2xl shadow-2xl flex flex-col border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white px-4 py-3 flex items-center gap-3 shrink-0 border-b border-cyan-500/30">
            <div className="w-9 h-9 rounded-full overflow-hidden border-2 border-cyan-400 shrink-0">
              <ThothIcon size={36} />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-sm text-cyan-300">Thoth-Legal Agent</p>
              <p className="text-xs text-slate-400">SYS Steel Compliance Bot</p>
            </div>
            <button onClick={() => setOpen(false)} className="hover:bg-slate-700 rounded p-1 transition-colors">
              <ChevronDown size={18} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-2 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${m.role === 'user' ? 'bg-blue-100' : 'bg-slate-900 border border-cyan-400/50 overflow-hidden'}`}>
                  {m.role === 'user' ? <User size={14} className="text-blue-600" /> : <ThothIcon size={28} />}
                </div>
                <div className={`max-w-[85%] ${m.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                  {/* Bubble */}
                  <div className={`rounded-2xl px-3 py-2 ${
                    m.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-sm text-sm'
                      : 'bg-gray-100 text-gray-800 rounded-tl-sm'
                  }`}>
                    {m.role === 'user'
                      ? <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                      : <MarkdownMessage content={m.content} />
                    }
                  </div>
                  {/* Law update cards below the bubble */}
                  {m.updates?.map((u, j) => <LawUpdateCard key={j} update={u} />)}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-2">
                <div className="w-7 h-7 rounded-full bg-slate-900 border border-cyan-400/50 overflow-hidden flex items-center justify-center">
                  <ThothIcon size={28} />
                </div>
                <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
                  <Loader2 size={14} className="animate-spin text-gray-400" />
                  <span className="text-xs text-gray-400">กำลังวิเคราะห์...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-3 flex gap-2 shrink-0">
            <textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKey}
              placeholder="ถามเกี่ยวกับกฏหมาย หรือพิมพ์ 'อัปเดตกฏหมาย'..."
              rows={1}
              className="flex-1 resize-none border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <button onClick={send} disabled={!input.trim() || loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-xl px-3 py-2 transition-colors">
              <Send size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
