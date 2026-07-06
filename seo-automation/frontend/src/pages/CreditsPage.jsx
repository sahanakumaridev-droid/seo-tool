/**
 * CreditsPage — Buy credits, view balance, transaction history
 */
import { useState, useEffect } from 'react'
import { Zap, CreditCard, History, CheckCircle, Loader2 } from 'lucide-react'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'
const api  = axios.create({ baseURL: BASE })
function getToken() { return localStorage.getItem('mp_token') }

const PACKAGE_COLORS = {
  starter: 'border-slate-500/30 bg-slate-500/5',
  growth:  'border-indigo-500/30 bg-indigo-500/5',
  pro:     'border-violet-500/30 bg-violet-500/5',
  agency:  'border-amber-500/30  bg-amber-500/5',
}
const PACKAGE_BADGE = {
  starter: null,
  growth:  'Most Popular',
  pro:     'Best Value',
  agency:  'For Agencies',
}

export default function CreditsPage() {
  const [packages, setPackages]   = useState([])
  const [balance, setBalance]     = useState(null)
  const [history, setHistory]     = useState([])
  const [buying, setBuying]       = useState('')
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [pkgRes, balRes, histRes] = await Promise.all([
          api.get('/marketplace/credits/packages'),
          api.get('/marketplace/credits/balance', { headers: { Authorization: `Bearer ${getToken()}` } }),
          api.get('/marketplace/credits/history',  { headers: { Authorization: `Bearer ${getToken()}` } }),
        ])
        setPackages(pkgRes.data)
        setBalance(balRes.data.credits)
        setHistory(histRes.data)
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  const handleBuy = async (packageId) => {
    setBuying(packageId)
    try {
      const res = await api.post('/marketplace/credits/purchase',
        { package_id: packageId },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      )
      setBalance(res.data.new_balance)
      // Refresh history
      const histRes = await api.get('/marketplace/credits/history', {
        headers: { Authorization: `Bearer ${getToken()}` }
      })
      setHistory(histRes.data)
      alert(`✅ ${res.data.credits_added} credits added! New balance: ${res.data.new_balance}`)
    } catch (err) {
      alert(err.response?.data?.detail || 'Purchase failed')
    } finally {
      setBuying('')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 size={24} className="animate-spin" style={{ color: 'var(--brand)' }} />
      </div>
    )
  }

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>Credits</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
            Buy credits to respond to leads and unlock premium features
          </p>
        </div>
        <div className="card px-5 py-3 flex items-center gap-2">
          <Zap size={16} className="text-amber-400" />
          <span className="text-xl font-bold" style={{ color: 'var(--text-1)' }}>{balance ?? '—'}</span>
          <span className="text-sm" style={{ color: 'var(--text-3)' }}>credits</span>
        </div>
      </div>

      {/* How it works */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-1)' }}>How Credits Work</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { icon: '🎯', title: 'Browse Free', desc: 'View all client requests at no cost' },
            { icon: '⚡', title: '2 Credits per Lead', desc: 'Spend 2 credits to submit a quote to a client' },
            { icon: '🏆', title: 'Win Projects', desc: 'Get hired and grow your business' },
          ].map(item => (
            <div key={item.title} className="text-center p-3 rounded-xl" style={{ background: 'var(--bg-raised)' }}>
              <div className="text-2xl mb-2">{item.icon}</div>
              <p className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>{item.title}</p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-3)' }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Packages */}
      <div>
        <h2 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-1)' }}>Choose a Package</h2>
        <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
          {packages.map(pkg => (
            <div
              key={pkg.id}
              className={`card p-5 space-y-3 relative border ${PACKAGE_COLORS[pkg.id] || ''}`}
            >
              {PACKAGE_BADGE[pkg.id] && (
                <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 text-[10px] px-2 py-0.5 rounded-full font-semibold bg-indigo-500 text-white">
                  {PACKAGE_BADGE[pkg.id]}
                </span>
              )}
              <div>
                <p className="text-sm font-bold" style={{ color: 'var(--text-1)' }}>{pkg.name}</p>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>{pkg.description}</p>
              </div>
              <div className="flex items-end gap-1">
                <span className="text-3xl font-bold" style={{ color: 'var(--brand)' }}>{pkg.credits}</span>
                <span className="text-sm mb-1" style={{ color: 'var(--text-3)' }}>credits</span>
              </div>
              <p className="text-lg font-semibold" style={{ color: 'var(--text-1)' }}>${pkg.price_usd}</p>
              <p className="text-[11px]" style={{ color: 'var(--text-3)' }}>
                ${(pkg.price_usd / pkg.credits).toFixed(2)} per credit
              </p>
              <button
                onClick={() => handleBuy(pkg.id)}
                disabled={buying === pkg.id}
                className="w-full btn-primary py-2 rounded-lg text-sm text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-1.5"
              >
                {buying === pkg.id
                  ? <><Loader2 size={13} className="animate-spin" /> Processing...</>
                  : <><CreditCard size={13} /> Buy Now</>
                }
              </button>
            </div>
          ))}
        </div>
        <p className="text-xs mt-3" style={{ color: 'var(--text-4)' }}>
          * Stripe payment integration required for production. Currently in demo mode — credits are added instantly.
        </p>
      </div>

      {/* Transaction history */}
      <div className="card">
        <div className="flex items-center gap-2 px-5 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
          <History size={14} style={{ color: 'var(--text-3)' }} />
          <h2 className="text-sm font-semibold" style={{ color: 'var(--text-1)' }}>Transaction History</h2>
        </div>
        {history.length === 0 ? (
          <div className="py-10 text-center">
            <p className="text-sm" style={{ color: 'var(--text-3)' }}>No transactions yet</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Description</th>
                <th>Amount</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {history.map(t => (
                <tr key={t.id}>
                  <td style={{ color: 'var(--text-2)' }}>{t.description}</td>
                  <td>
                    <span className={t.amount > 0 ? 'text-emerald-400' : 'text-red-400'}>
                      {t.amount > 0 ? '+' : ''}{t.amount}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-3)' }}>
                    {t.created_at ? new Date(t.created_at).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
