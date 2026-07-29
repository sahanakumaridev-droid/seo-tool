import { Check } from 'lucide-react'
import { PRICING_TIERS } from '../../data/mockData'

export default function PricingPreview({ onSelect }) {
  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {PRICING_TIERS.map(tier => (
        <div
          key={tier.name}
          className="card"
          style={{
            padding: 28,
            borderColor: tier.featured ? 'var(--brand)' : 'var(--border)',
            boxShadow: tier.featured ? '0 16px 40px rgba(255,90,78,0.14)' : 'var(--shadow-sm)',
            position: 'relative',
          }}
        >
          {tier.featured && (
            <span style={{ position: 'absolute', top: -12, left: 24, fontSize: 11, fontWeight: 700, color: '#fff', background: 'var(--brand)', padding: '3px 10px', borderRadius: 999 }}>
              Most Popular
            </span>
          )}
          <h3 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-1)', margin: '4px 0 6px' }}>{tier.name}</h3>
          <p style={{ fontSize: 13, color: 'var(--text-3)', margin: '0 0 18px', minHeight: 36 }}>{tier.desc}</p>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 20 }}>
            <span className="font-display" style={{ fontSize: 34, fontWeight: 800, color: 'var(--text-1)' }}>{tier.price}</span>
            <span style={{ fontSize: 13, color: 'var(--text-3)' }}>{tier.period}</span>
          </div>
          <button
            onClick={onSelect}
            className={tier.featured ? 'btn btn-primary' : 'btn btn-secondary'}
            style={{ width: '100%', marginBottom: 22, padding: '11px 16px' }}
          >
            Start Free Trial
          </button>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {tier.features.map(f => (
              <div key={f} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--text-2)' }}>
                <Check size={14} style={{ color: 'var(--green)', flexShrink: 0 }} /> {f}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
