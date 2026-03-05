import { useState, useRef, useEffect, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { X, Send, Loader2, User, ChevronDown, PlusCircle, Trash2,
         RefreshCw, Settings, Check, Copy, CheckCheck, Maximize2,
         Minimize2, History, ArrowLeft, Search, MessageSquarePlus } from 'lucide-react'

const API = 'http://localhost:8000'

const ThothIcon = ({ size = 20 }) => (
  <img src="/thoth.png" alt="Thoth" width={size} height={size}
    className="rounded-full object-cover w-full h-full"
    onError={e => { e.target.style.display = 'none' }} />
)

const PROVIDERS = {
  anthropic:  { label: 'Anthropic Claude', color: 'text-orange-400', models: ['claude-opus-4-5','claude-sonnet-4-5','claude-haiku-3-5'] },
  openai:     { label: 'OpenAI', color: 'text-green-400', models: ['gpt-5.2','o3','o3-mini','o1','o1-mini','gpt-4o','gpt-4o-mini','gpt-4-turbo'] },
  bedrock:    { label: 'AWS Bedrock', color: 'text-yellow-400', models: ['apac.anthropic.claude-sonnet-4-5-v1:0','anthropic.claude-3-5-sonnet-20241022-v2:0','anthropic.claude-3-haiku-20240307-v1:0','meta.llama3-70b-instruct-v1:0'] },
  grok:       { label: 'Grok (xAI)', color: 'text-purple-400', models: ['grok-3','grok-3-mini','grok-2'] },
  ollama:     { label: 'Ollama (Local)', color: 'text-cyan-400', models: ['llama3.2','llama3.1','mistral','qwen2.5'] },
  openrouter: { label: 'OpenRouter', color: 'text-pink-400', models: ['anthropic/claude-3.5-sonnet','openai/gpt-4o','google/gemini-pro','meta-llama/llama-3.1-70b-instruct'] },
}

const RISK_COLOR = {
  critical:'bg-red-100 text-red-700 border-red-200', high:'bg-orange-100 text-orange-700 border-orange-200',
  medium:'bg-yellow-100 text-yellow-700 border-yellow-200', low:'bg-green-100 text-green-700 border-green-200',
}
const RISK_LABEL = { critical:'🔴 Critical', high:'🟠 High', medium:'🟡 Medium', low:'🟢 Low' }

// ── Copy Button ────────────────────────────────────────────────────────────────
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  function handleCopy() {
    navigator.clipboard.writeText(text).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000) })
  }
  return (
    <button onClick={handleCopy} title={copied ? 'Copied!' : 'Copy'}
      className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
      {copied ? <CheckCheck size={13} className="text-green-500" /> : <Copy size={13} />}
      {copied ? <span className="text-green-500">Copied</span> : <span>Copy</span>}
    </button>
  )
}

// ── Law Update Card ────────────────────────────────────────────────────────────
function LawUpdateCard({ update }) {
  const a = update.action
  if (a === 'add_law') return (
    <div className="mt-2 rounded-xl border border-green-200 bg-green-50 p-3 text-xs space-y-1.5">
      <div className="flex items-center gap-1.5 font-semibold text-green-700"><PlusCircle size={13}/>เพิ่มกฏหมายใหม่</div>
      <p className="font-bold text-gray-800">[{update.law_code}] {update.name_th}</p>
      {update.description && <p className="text-gray-600">{update.description}</p>}
      <div className="flex flex-wrap gap-1.5">
        {update.risk_level && <span className={`px-2 py-0.5 rounded-full border ${RISK_COLOR[update.risk_level]}`}>{RISK_LABEL[update.risk_level]}</span>}
        {update.effective_date && <span className="px-2 py-0.5 rounded-full border bg-blue-50 text-blue-700 border-blue-200">มีผล {update.effective_date}</span>}
        {update.matrix_created > 0 && <span className="px-2 py-0.5 rounded-full border bg-slate-100 text-slate-600 border-slate-200">Matrix {update.matrix_created} หน่วยงาน</span>}
        {update.tasks_created > 0 && <span className="px-2 py-0.5 rounded-full border bg-purple-50 text-purple-700 border-purple-200">Tasks {update.tasks_created} รายการ</span>}
      </div>
      {update.penalty_summary && <p className="text-red-600">⚠️ {update.penalty_summary}</p>}
    </div>
  )
  if (a === 'update_law') return (
    <div className="mt-2 rounded-xl border border-blue-200 bg-blue-50 p-3 text-xs space-y-1.5">
      <div className="flex items-center gap-1.5 font-semibold text-blue-700"><RefreshCw size={13}/>อัปเดตกฏหมาย [{update.law_code}]</div>
      {update.summary && <p className="text-gray-700">{update.summary}</p>}
      {update.changes && <div>{update.changes.old && <p className="line-through text-gray-400">{update.changes.old}</p>}{update.changes.new && <p className="font-medium">{update.changes.new}</p>}</div>}
      {update.source && <p className="text-gray-400">📎 {update.source}</p>}
    </div>
  )
  if (a === 'remove_law') return (
    <div className="mt-2 rounded-xl border border-red-200 bg-red-50 p-3 text-xs space-y-1.5">
      <div className="flex items-center gap-1.5 font-semibold text-red-700"><Trash2 size={13}/>ลบกฏหมาย [{update.law_code}]</div>
      {update.law_name && <p className="text-gray-700">{update.law_name}</p>}
      {update.reason && <p className="text-gray-500">{update.reason}</p>}
      {update.removed === true && <p className="text-red-600 font-medium">✓ ลบออกจากระบบแล้ว</p>}
    </div>
  )
  return null
}

// ── Markdown Message ───────────────────────────────────────────────────────────
function MarkdownMessage({ content }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
      table: ({children}) => <div className="overflow-x-auto my-2 rounded-lg border border-gray-200"><table className="text-xs w-full border-collapse">{children}</table></div>,
      thead: ({children}) => <thead className="bg-slate-700 text-white">{children}</thead>,
      tbody: ({children}) => <tbody className="divide-y divide-gray-100">{children}</tbody>,
      th: ({children}) => <th className="px-3 py-2 text-left font-medium whitespace-nowrap">{children}</th>,
      td: ({children}) => <td className="px-3 py-2 text-gray-700">{children}</td>,
      tr: ({children}) => <tr className="hover:bg-gray-50">{children}</tr>,
      code: ({inline,children}) => inline
        ? <code className="bg-gray-200 text-red-600 px-1 rounded text-xs font-mono">{children}</code>
        : <pre className="bg-gray-800 text-green-300 rounded-lg p-3 text-xs overflow-x-auto my-2 font-mono"><code>{children}</code></pre>,
      strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
      ul: ({children}) => <ul className="list-disc list-inside space-y-0.5 my-1">{children}</ul>,
      ol: ({children}) => <ol className="list-decimal list-inside space-y-0.5 my-1">{children}</ol>,
      li: ({children}) => <li className="text-sm leading-relaxed">{children}</li>,
      p: ({children}) => <p className="text-sm leading-relaxed mb-1 last:mb-0">{children}</p>,
      h1: ({children}) => <p className="font-bold text-base text-gray-900 mt-2 mb-1">{children}</p>,
      h2: ({children}) => <p className="font-bold text-sm text-gray-800 mt-2 mb-1">{children}</p>,
      h3: ({children}) => <p className="font-semibold text-sm text-gray-700 mt-1 mb-0.5">{children}</p>,
      blockquote: ({children}) => <div className="border-l-4 border-blue-400 bg-blue-50 pl-3 py-1 my-1 rounded-r-lg text-blue-800 text-xs">{children}</div>,
      hr: () => <hr className="my-2 border-gray-200" />,
    }}>{content}</ReactMarkdown>
  )
}

// ── Provider Panel ─────────────────────────────────────────────────────────────
function ProviderPanel({ current, onClose, onSave }) {
  const [selProvider, setSelProvider] = useState(current?.provider || 'anthropic')
  const [selModel, setSelModel] = useState(current?.model || '')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    setSelModel(current?.provider === selProvider ? (current?.model || PROVIDERS[selProvider]?.models[0] || '') : (PROVIDERS[selProvider]?.models[0] || ''))
  }, [selProvider])

  async function handleSave() {
    setSaving(true)
    try {
      const r = await fetch(`${API}/api/chat/provider`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({provider:selProvider,model:selModel}) })
      onSave(await r.json()); setSaved(true); setTimeout(() => { setSaved(false); onClose() }, 800)
    } catch { alert('เปลี่ยน provider ไม่สำเร็จ') }
    setSaving(false)
  }

  return (
    <div className="absolute inset-0 bg-slate-950/95 z-10 flex flex-col p-4 rounded-2xl overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <p className="text-cyan-300 font-semibold text-sm">เลือก LLM Provider</p>
        <button onClick={onClose} className="text-slate-400 hover:text-white"><X size={16}/></button>
      </div>
      <div className="space-y-1.5 mb-4">
        {Object.entries(PROVIDERS).map(([key,cfg]) => (
          <button key={key} onClick={() => setSelProvider(key)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${selProvider===key?'bg-slate-700 ring-1 ring-cyan-500':'hover:bg-slate-800'}`}>
            <span className={`w-2 h-2 rounded-full ${selProvider===key?'bg-cyan-400':'bg-slate-600'}`}/>
            <span className={`text-sm font-medium ${cfg.color}`}>{cfg.label}</span>
            {selProvider===key && <Check size={13} className="ml-auto text-cyan-400"/>}
          </button>
        ))}
      </div>
      <p className="text-xs text-slate-400 mb-1.5">Model</p>
      <select value={selModel} onChange={e => setSelModel(e.target.value)}
        className="w-full bg-slate-800 text-white text-xs rounded-lg px-3 py-2 border border-slate-600 focus:outline-none focus:ring-1 focus:ring-cyan-500 mb-1.5">
        {PROVIDERS[selProvider]?.models.map(m => <option key={m} value={m}>{m}</option>)}
      </select>
      <input value={selModel} onChange={e => setSelModel(e.target.value)} placeholder="หรือพิมพ์ชื่อ model เอง..."
        className="w-full bg-slate-800 text-white text-xs rounded-lg px-3 py-2 border border-slate-600 focus:outline-none focus:ring-1 focus:ring-cyan-500 placeholder-slate-500 mb-4"/>
      <button onClick={handleSave} disabled={saving||saved}
        className={`w-full py-2.5 rounded-xl text-sm font-medium transition-colors ${saved?'bg-green-600 text-white':'bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-50'}`}>
        {saved?'✓ บันทึกแล้ว':saving?'กำลังบันทึก...':'บันทึก'}
      </button>
    </div>
  )
}

// ── History Panel ──────────────────────────────────────────────────────────────
function HistoryPanel({ username, onClose, onLoadSession }) {
  const [sessions, setSessions] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/api/chat/sessions?username=${encodeURIComponent(username)}`)
      .then(r => r.json()).then(setSessions).finally(() => setLoading(false))
  }, [username])

  async function handleDelete(sid, e) {
    e.stopPropagation()
    if (!confirm('ลบประวัติ chat นี้?')) return
    await fetch(`${API}/api/chat/sessions/${sid}`, { method: 'DELETE' })
    setSessions(s => s.filter(x => x.session_id !== sid))
  }

  const filtered = sessions.filter(s => s.title?.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="absolute inset-0 bg-white z-10 flex flex-col rounded-2xl overflow-hidden">
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 px-4 py-3 flex items-center gap-2 shrink-0">
        <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded"><ArrowLeft size={16}/></button>
        <p className="text-cyan-300 font-semibold text-sm flex-1">ประวัติการสนทนา</p>
        <p className="text-xs text-slate-400">{username}</p>
      </div>
      <div className="p-3 border-b border-gray-100">
        <div className="relative">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400"/>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="ค้นหาประวัติ..."
            className="w-full pl-8 pr-3 py-1.5 border border-gray-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-300"/>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        {loading && <div className="p-4 text-center text-xs text-gray-400">กำลังโหลด...</div>}
        {!loading && filtered.length === 0 && <div className="p-4 text-center text-xs text-gray-400">ไม่มีประวัติการสนทนา</div>}
        {filtered.map(s => (
          <button key={s.session_id} onClick={() => onLoadSession(s.session_id)}
            className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-50 group flex items-start gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-800 truncate">{s.title || 'New Chat'}</p>
              <p className="text-xs text-gray-400 mt-0.5">{s.updated_at?.slice(0,16).replace('T',' ')}</p>
            </div>
            <button onClick={e => handleDelete(s.session_id, e)}
              className="opacity-0 group-hover:opacity-100 p-1 text-red-400 hover:text-red-600 rounded transition-opacity">
              <Trash2 size={13}/>
            </button>
          </button>
        ))}
      </div>
    </div>
  )
}

// ── Main ChatBot ───────────────────────────────────────────────────────────────
export default function ChatBot({ auth }) {
  const username = auth?.username || 'anonymous'
  const greeting = `สวัสดีครับคุณ **${username}** 👋\n\nผมคือ **Thoth-Legal Agent** พร้อมช่วยด้านกฏหมายของ SYS Steel\n\nสามารถถามเกี่ยวกับ:\n- รายละเอียดกฏหมายในระบบ\n- ผลกระทบต่อหน่วยงาน\n- พิมพ์ **"อัปเดตกฏหมาย"** เพื่อค้นหาการเปลี่ยนแปลงล่าสุด`

  const [open, setOpen] = useState(false)
  const [maximized, setMaximized] = useState(false)
  const [panel, setPanel] = useState(null) // null | 'settings' | 'history'
  const [messages, setMessages] = useState([{ role:'assistant', content: greeting, updates:[] }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [totalUpdates, setTotalUpdates] = useState(0)
  const [provider, setProvider] = useState(null)
  const bottomRef = useRef(null)
  const abortControllerRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/api/chat/provider`).then(r => r.json()).then(setProvider).catch(() => {})
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior:'smooth' })
  }, [messages, open])

  function newChat() {
    setSessionId(null)
    setMessages([{ role:'assistant', content: greeting, updates:[] }])
    setPanel(null)
  }

  async function loadSession(sid) {
    const msgs = await fetch(`${API}/api/chat/sessions/${sid}`).then(r => r.json())
    setSessionId(sid)
    setMessages([
      { role:'assistant', content: greeting, updates:[] },
      ...msgs.map(m => ({ role:m.role, content:m.content, updates:m.law_updates||[] }))
    ])
    setPanel(null)
  }

  function stopGeneration() {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setLoading(false)
    setMessages(prev => [...prev, { role:'assistant', content:'⚠️ การประมวลผลถูกยกเลิก', updates:[] }])
  }

  async function send() {
    const msg = input.trim()
    if (!msg || loading) return
    setInput('')
    const history = messages.filter(m => m.role !== 'system').slice(-10).map(m => ({ role:m.role, content:m.content }))
    setMessages(prev => [...prev, { role:'user', content:msg, updates:[] }])
    setLoading(true)
    
    abortControllerRef.current = new AbortController()
    
    try {
      const res = await fetch(`${API}/api/chat`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ message:msg, session_id:sessionId, username, history }),
        signal: abortControllerRef.current.signal
      })
      const data = await res.json()
      setSessionId(data.session_id)
      const cleanReply = data.reply.replace(/<law_update>[\s\S]*?<\/law_update>/g,'').trim()
      const updates = data.law_updates || []
      setMessages(prev => [...prev, { role:'assistant', content:cleanReply, updates }])
      if (updates.length > 0) setTotalUpdates(n => n + updates.length)
    } catch (err) {
      if (err.name === 'AbortError') return // User cancelled
      setMessages(prev => [...prev, { role:'assistant', content:'⚠️ ไม่สามารถเชื่อมต่อกับ server ได้', updates:[] }])
    } finally {
      abortControllerRef.current = null
      setLoading(false)
    }
  }

  function handleKey(e) { if (e.key==='Enter' && !e.shiftKey) { e.preventDefault(); send() } }

  const providerCfg = provider ? PROVIDERS[provider.provider] : null

  // Window size classes
  const windowCls = maximized
    ? 'fixed inset-4 z-50 flex flex-col bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden'
    : 'fixed bottom-24 right-6 z-50 w-[420px] max-h-[640px] flex flex-col bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden'

  return (
    <>
      {/* Floating button */}
      <button onClick={() => { setOpen(o => !o); setTotalUpdates(0) }}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-slate-900 hover:bg-slate-800 rounded-full shadow-lg flex items-center justify-center transition-all overflow-hidden border-2 border-cyan-400"
        title="Thoth-Legal Agent">
        {open ? <X size={22} className="text-white"/> : <ThothIcon size={48}/>}
        {!open && totalUpdates > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">{totalUpdates}</span>
        )}
      </button>

      {open && (
        <div className={windowCls}>
          {/* Panels overlay */}
          {panel === 'settings' && <ProviderPanel current={provider} onClose={() => setPanel(null)} onSave={d => { setProvider(d); setPanel(null) }}/>}
          {panel === 'history' && <HistoryPanel username={username} onClose={() => setPanel(null)} onLoadSession={loadSession}/>}

          {/* Header */}
          <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white px-4 py-3 flex items-center gap-2 shrink-0 border-b border-cyan-500/30">
            <div className="w-9 h-9 rounded-full overflow-hidden border-2 border-cyan-400 shrink-0">
              <ThothIcon size={36}/>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm text-cyan-300">Thoth-Legal Agent</p>
              <p className={`text-xs truncate ${providerCfg?.color||'text-slate-400'}`}>
                {provider ? `${PROVIDERS[provider.provider]?.label||provider.provider} · ${provider.model}` : 'SYS Steel Compliance Bot'}
              </p>
            </div>
            {/* New chat */}
            <button onClick={newChat} title="สนทนาใหม่" className="hover:bg-slate-700 rounded-lg p-1.5 transition-colors text-slate-400 hover:text-cyan-300"><MessageSquarePlus size={15}/></button>
            {/* History */}
            <button onClick={() => setPanel(p => p==='history'?null:'history')} title="ประวัติการสนทนา" className={`hover:bg-slate-700 rounded-lg p-1.5 transition-colors ${panel==='history'?'text-cyan-300':'text-slate-400 hover:text-cyan-300'}`}><History size={15}/></button>
            {/* Settings */}
            <button onClick={() => setPanel(p => p==='settings'?null:'settings')} title="เปลี่ยน LLM Provider" className={`hover:bg-slate-700 rounded-lg p-1.5 transition-colors ${panel==='settings'?'text-cyan-300':'text-slate-400 hover:text-cyan-300'}`}><Settings size={15}/></button>
            {/* Maximize */}
            <button onClick={() => setMaximized(m => !m)} title={maximized?'ย่อ':'ขยาย'} className="hover:bg-slate-700 rounded-lg p-1.5 transition-colors text-slate-400 hover:text-cyan-300">
              {maximized ? <Minimize2 size={15}/> : <Maximize2 size={15}/>}
            </button>
            <button onClick={() => setOpen(false)} className="hover:bg-slate-700 rounded p-1 transition-colors"><ChevronDown size={18}/></button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-2 ${m.role==='user'?'flex-row-reverse':''}`}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${m.role==='user'?'bg-blue-100':'bg-slate-900 border border-cyan-400/50 overflow-hidden'}`}>
                  {m.role==='user' ? <User size={14} className="text-blue-600"/> : <ThothIcon size={28}/>}
                </div>
                <div className={`max-w-[85%] flex flex-col gap-1 ${m.role==='user'?'items-end':'items-start'}`}>
                  <div className={`rounded-2xl px-3 py-2 ${m.role==='user'?'bg-blue-600 text-white rounded-tr-sm':'bg-gray-100 text-gray-800 rounded-tl-sm'}`}>
                    {m.role==='user'
                      ? <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                      : <MarkdownMessage content={m.content}/>}
                  </div>
                  {m.role==='assistant' && <CopyButton text={m.content}/>}
                  {m.updates?.map((u,j) => <LawUpdateCard key={j} update={u}/>)}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-2">
                <div className="w-7 h-7 rounded-full bg-slate-900 border border-cyan-400/50 overflow-hidden flex items-center justify-center"><ThothIcon size={28}/></div>
                <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
                  <Loader2 size={14} className="animate-spin text-gray-400"/>
                  <span className="text-xs text-gray-400">กำลังวิเคราะห์...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef}/>
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-3 flex gap-2 shrink-0">
            <textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKey}
              placeholder="ถามเกี่ยวกับกฏหมาย หรือพิมพ์ 'อัปเดตกฏหมาย'..."
              disabled={loading}
              rows={1} className="flex-1 resize-none border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"/>
            {loading ? (
              <button onClick={stopGeneration}
                className="bg-red-600 hover:bg-red-700 text-white rounded-xl px-3 py-2 transition-colors flex items-center gap-1.5">
                <X size={16}/>
                <span className="text-sm font-medium">หยุด</span>
              </button>
            ) : (
              <button onClick={send} disabled={!input.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-xl px-3 py-2 transition-colors">
                <Send size={16}/>
              </button>
            )}
          </div>
        </div>
      )}
    </>
  )
}
