import { useParams, useNavigate } from 'react-router-dom'
import { Construction, ArrowLeft } from 'lucide-react'
import { COMING_SOON_MODULES } from '../data/comingSoonModules'

export default function ComingSoonPage() {
  const { module } = useParams()
  const navigate = useNavigate()
  const copy = COMING_SOON_MODULES[module] || { title: 'Coming Soon', description: 'This module is on its way.' }

  return (
    <div className="card fade-in flex flex-col items-center justify-center text-center" style={{ padding: '80px 24px', maxWidth: 480, margin: '40px auto' }}>
      <div style={{ width: 56, height: 56, borderRadius: 14, background: 'var(--brand-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Construction size={26} style={{ color: 'var(--brand)' }} />
      </div>
      <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-1)', margin: '18px 0 8px' }}>{copy.title}</h1>
      <p style={{ fontSize: 13.5, color: 'var(--text-3)', lineHeight: 1.6, margin: '0 0 22px' }}>{copy.description}</p>
      <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--brand-dark)', background: 'var(--brand-soft)', padding: '4px 12px', borderRadius: 999, marginBottom: 22 }}>Coming Soon</span>
      <button onClick={() => navigate('/content')} className="btn btn-secondary">
        <ArrowLeft size={14} /> Back to SEO Content
      </button>
    </div>
  )
}
