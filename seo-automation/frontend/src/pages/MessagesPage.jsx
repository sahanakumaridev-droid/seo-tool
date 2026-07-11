/**
 * MessagesPage — In-app messaging between clients and professionals
 */
import { useState, useEffect, useRef } from 'react'
import { MessageSquare, Send, Loader2, User } from 'lucide-react'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api  = axios.create({ baseURL: BASE })

function getToken() { return localStorage.getItem('mp_token') }
function getUser()  {
  try { return JSON.parse(localStorage.getItem('mp_user') || '{}') } catch { return {} }
}

function MessageBubble({ msg, isOwn }) {
  return (
    <div className={`flex gap-2 ${isOwn ? 'flex-row-reverse' : ''}`}>
      <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ background: isOwn ? 'var(--brand)' : 'var(--bg-raised)', border: '1px solid var(--border)' }}>
        <User size={12} style={{ color: isOwn ? '#fff' : 'var(--text-3)' }} />
      </div>
      <div className={`max-w-[70%] rounded-2xl px-3 py-2 ${isOwn ? 'rounded-tr-sm' : 'rounded-tl-sm'}`}
        style={{
          background: isOwn ? 'var(--brand)' : 'var(--bg-raised)',
          border: isOwn ? 'none' : '1px solid var(--border)',
        }}>
        {!isOwn && (
          <p className="text-[10px] font-semibold mb-0.5" style={{ color: 'var(--text-3)' }}>{msg.sender_name}</p>
        )}
        <p className="text-sm" style={{ color: isOwn ? '#fff' : 'var(--text-1)' }}>{msg.content}</p>
        <p className="text-[10px] mt-0.5 text-right" style={{ color: isOwn ? 'rgba(255,255,255,0.6)' : 'var(--text-4)' }}>
          {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
        </p>
      </div>
    </div>
  )
}

export default function MessagesPage() {
  const [messages, setMessages]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [newMsg, setNewMsg]       = useState('')
  const [recipientId, setRecipientId] = useState('')
  const [sending, setSending]     = useState(false)
  const bottomRef = useRef(null)
  const currentUser = getUser()

  const loadMessages = async () => {
    try {
      const res = await api.get('/marketplace/messages/inbox', {
        headers: { Authorization: `Bearer ${getToken()}` }
      })
      setMessages(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => {
    loadMessages()
    const interval = setInterval(loadMessages, 15000)  // poll every 15s
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!newMsg.trim() || !recipientId) return
    setSending(true)
    try {
      const res = await api.post('/marketplace/messages', {
        recipient_id: parseInt(recipientId),
        content: newMsg.trim(),
      }, { headers: { Authorization: `Bearer ${getToken()}` } })
      setMessages(prev => [...prev, res.data])
      setNewMsg('')
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to send message')
    } finally {
      setSending(false)
    }
  }

  const markRead = async (msgId) => {
    try {
      await api.patch(`/marketplace/messages/${msgId}/read`, {}, {
        headers: { Authorization: `Bearer ${getToken()}` }
      })
      setMessages(prev => prev.map(m => m.id === msgId ? { ...m, read: true } : m))
    } catch (e) { /* silent */ }
  }

  const unread = messages.filter(m => !m.read).length

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>Messages</h1>
        <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
          Chat with clients and professionals
          {unread > 0 && <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400">{unread} unread</span>}
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-4" style={{ height: 'calc(100vh - 220px)', minHeight: 400 }}>
        {/* Inbox list */}
        <div className="card overflow-y-auto">
          <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
            <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-3)' }}>Inbox</p>
          </div>
          {loading ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 size={20} className="animate-spin" style={{ color: 'var(--brand)' }} />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10">
              <MessageSquare size={28} className="mb-2 opacity-20" style={{ color: 'var(--text-3)' }} />
              <p className="text-xs" style={{ color: 'var(--text-3)' }}>No messages yet</p>
            </div>
          ) : (
            <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
              {messages.map(msg => (
                <div
                  key={msg.id}
                  onClick={() => markRead(msg.id)}
                  className="px-4 py-3 cursor-pointer transition-colors hover:bg-white/3"
                  style={{ background: !msg.read ? 'var(--brand-soft)' : 'transparent' }}
                >
                  <div className="flex items-center justify-between mb-0.5">
                    <p className="text-xs font-semibold" style={{ color: 'var(--text-1)' }}>{msg.sender_name}</p>
                    {!msg.read && <span className="w-2 h-2 rounded-full bg-indigo-500" />}
                  </div>
                  <p className="text-xs truncate" style={{ color: 'var(--text-3)' }}>{msg.content}</p>
                  <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-4)' }}>
                    {msg.created_at ? new Date(msg.created_at).toLocaleDateString() : ''}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Compose / thread */}
        <div className="lg:col-span-2 card flex flex-col">
          <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
            <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-3)' }}>New Message</p>
          </div>

          {/* Message thread area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map(msg => (
              <MessageBubble
                key={msg.id}
                msg={msg}
                isOwn={msg.sender_id === currentUser.id}
              />
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Compose */}
          <form onSubmit={handleSend} className="p-4 border-t space-y-2" style={{ borderColor: 'var(--border)' }}>
            <div className="flex gap-2">
              <input
                type="number"
                value={recipientId}
                onChange={e => setRecipientId(e.target.value)}
                placeholder="Recipient User ID"
                className="w-32 rounded-lg px-3 py-2 text-sm"
                style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
              />
              <input
                value={newMsg}
                onChange={e => setNewMsg(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 rounded-lg px-3 py-2 text-sm"
                style={{ background: 'var(--bg-raised)', border: '1px solid var(--border)', color: 'var(--text-1)' }}
              />
              <button
                type="submit"
                disabled={sending || !newMsg.trim() || !recipientId}
                className="btn-primary px-4 py-2 rounded-lg text-white disabled:opacity-50 flex items-center gap-1"
              >
                {sending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
              </button>
            </div>
            <p className="text-[10px]" style={{ color: 'var(--text-4)' }}>
              Enter the recipient's user ID to start a conversation
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
