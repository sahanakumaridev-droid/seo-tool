/**
 * AdminPage — Platform admin: stats, user management, approvals
 */
import { useState, useEffect } from 'react'
import {
  Users, Briefcase, MessageSquare, Zap, CheckCircle,
  Shield, TrendingUp, RefreshCw
} from 'lucide-react'
import axios from 'axios'
import BrandLoader from '../components/BrandLoader'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api  = axios.create({ baseURL: BASE })
function getToken() { return localStorage.getItem('mp_token') }

function StatBox({ label, value, icon, color }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-3)' }}>{label}</span>
        <span className={color}>{icon}</span>
      </div>
      <p className="text-3xl font-bold" style={{ color: 'var(--text-1)' }}>{value ?? '—'}</p>
    </div>
  )
}

export default function AdminPage() {
  const [stats, setStats]   = useState(null)
  const [users, setUsers]   = useState([])
  const [loading, setLoading] = useState(true)
  const [verifying, setVerifying] = useState(null)
  const [newUser, setNewUser] = useState({ name: '', email: '', password: '', role: 'client' })
  const [creating, setCreating] = useState(false)
  const [createMsg, setCreateMsg] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const headers = { Authorization: `Bearer ${getToken()}` }
      const [statsRes, usersRes] = await Promise.all([
        api.get('/marketplace/admin/stats', { headers }),
        api.get('/marketplace/admin/users', { headers }),
      ])
      setStats(statsRes.data)
      setUsers(usersRes.data)
    } catch (e) {
      console.error(e)
      if (e.response?.status === 403) {
        alert('Admin access required')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleVerify = async (userId) => {
    setVerifying(userId)
    try {
      await api.patch(`/marketplace/admin/users/${userId}/verify`, {}, {
        headers: { Authorization: `Bearer ${getToken()}` }
      })
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_verified: true } : u))
    } catch (e) { alert(e.response?.data?.detail || 'Failed to verify') }
    finally { setVerifying(null) }
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    setCreating(true)
    setCreateMsg('')
    try {
      await api.post('/users/register', {
        name: newUser.name.trim(),
        email: newUser.email.trim(),
        password: newUser.password,
        role: newUser.role,
      })
      setCreateMsg('User created. They can sign in on the SEO tool login page.')
      setNewUser({ name: '', email: '', password: '', role: 'client' })
      await load()
    } catch (err) {
      const detail = err.response?.data?.detail
      setCreateMsg(typeof detail === 'string' ? detail : 'Could not create user.')
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return <BrandLoader label="Loading admin…" />
  }

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold flex items-center gap-2" style={{ color: 'var(--text-1)' }}>
            <Shield size={18} style={{ color: 'var(--brand)' }} /> Admin Dashboard
          </h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>Platform overview and management</p>
        </div>
        <button onClick={load}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm"
          style={{ border: '1px solid var(--border)', color: 'var(--text-2)' }}>
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Stats grid */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatBox label="Total Users"    value={stats.total_users}         icon={<Users size={16} />}       color="text-indigo-400" />
          <StatBox label="Clients"        value={stats.total_clients}       icon={<Users size={16} />}       color="text-sky-400" />
          <StatBox label="Professionals"  value={stats.total_professionals} icon={<Briefcase size={16} />}   color="text-violet-400" />
          <StatBox label="Open Requests"  value={stats.open_requests}       icon={<TrendingUp size={16} />}  color="text-emerald-400" />
          <StatBox label="Total Requests" value={stats.total_requests}      icon={<Briefcase size={16} />}   color="text-amber-400" />
          <StatBox label="Total Quotes"   value={stats.total_quotes}        icon={<CheckCircle size={16} />} color="text-green-400" />
          <StatBox label="Messages Sent"  value={stats.total_messages}      icon={<MessageSquare size={16} />} color="text-pink-400" />
          <StatBox label="Credits Sold"   value={stats.total_credits_sold}  icon={<Zap size={16} />}         color="text-amber-400" />
        </div>
      )}

      {/* User management */}
      <div className="card">
        <div className="flex items-center justify-between px-5 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
          <h2 className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>Create SEO login</h2>
        </div>
        <form onSubmit={handleCreateUser} className="px-5 py-4 flex flex-wrap gap-3 items-end">
          <label className="text-xs" style={{ color: 'var(--text-2)' }}>
            Name
            <input required minLength={2} value={newUser.name} onChange={(e) => setNewUser((u) => ({ ...u, name: e.target.value }))}
              className="block mt-1 rounded-lg px-3 py-2 text-sm" style={{ border: '1px solid var(--border)', minWidth: 160 }} />
          </label>
          <label className="text-xs" style={{ color: 'var(--text-2)' }}>
            Email
            <input required type="email" value={newUser.email} onChange={(e) => setNewUser((u) => ({ ...u, email: e.target.value }))}
              className="block mt-1 rounded-lg px-3 py-2 text-sm" style={{ border: '1px solid var(--border)', minWidth: 200 }} />
          </label>
          <label className="text-xs" style={{ color: 'var(--text-2)' }}>
            Password (8+ chars)
            <input required minLength={8} type="password" value={newUser.password} onChange={(e) => setNewUser((u) => ({ ...u, password: e.target.value }))}
              className="block mt-1 rounded-lg px-3 py-2 text-sm" style={{ border: '1px solid var(--border)', minWidth: 160 }} />
          </label>
          <label className="text-xs" style={{ color: 'var(--text-2)' }}>
            Role
            <select value={newUser.role} onChange={(e) => setNewUser((u) => ({ ...u, role: e.target.value }))}
              className="block mt-1 rounded-lg px-3 py-2 text-sm" style={{ border: '1px solid var(--border)' }}>
              <option value="client">Client</option>
              <option value="admin">Admin</option>
              <option value="professional">Professional</option>
            </select>
          </label>
          <button type="submit" disabled={creating} className="px-4 py-2 rounded-lg text-sm text-white" style={{ background: 'var(--brand)' }}>
            {creating ? 'Creating…' : 'Create user'}
          </button>
          {createMsg && <p className="text-xs w-full m-0" style={{ color: 'var(--text-3)' }}>{createMsg}</p>}
        </form>
      </div>

      {/* User management */}
      <div className="card">
        <div className="flex items-center justify-between px-5 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
          <h2 className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>User Management</h2>
          <span className="text-xs" style={{ color: 'var(--text-3)' }}>{users.length} users</span>
        </div>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Credits</th>
                <th>Rating</th>
                <th>Verified</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td style={{ color: 'var(--text-3)' }}>#{u.id}</td>
                  <td className="font-medium" style={{ color: 'var(--text-1)' }}>{u.name}</td>
                  <td style={{ color: 'var(--text-2)' }}>{u.email}</td>
                  <td>
                    <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${
                      u.role === 'admin' ? 'text-red-400 bg-red-400/10' :
                      u.role === 'professional' ? 'text-violet-400 bg-violet-400/10' :
                      'text-sky-400 bg-sky-400/10'
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-2)' }}>{u.credits}</td>
                  <td style={{ color: 'var(--text-2)' }}>
                    {u.rating ? `${u.rating.toFixed(1)} ⭐` : '—'}
                  </td>
                  <td>
                    {u.is_verified
                      ? <CheckCircle size={14} className="text-emerald-400" />
                      : <span className="text-xs" style={{ color: 'var(--text-4)' }}>—</span>
                    }
                  </td>
                  <td style={{ color: 'var(--text-3)' }}>
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                  </td>
                  <td>
                    {u.role === 'professional' && !u.is_verified && (
                      <button
                        onClick={() => handleVerify(u.id)}
                        disabled={verifying === u.id}
                        className="text-xs px-2 py-1 rounded-lg text-emerald-400 border border-emerald-400/20 hover:bg-emerald-400/10 transition-colors disabled:opacity-50"
                      >
                        {verifying === u.id ? 'Verifying...' : 'Verify'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
