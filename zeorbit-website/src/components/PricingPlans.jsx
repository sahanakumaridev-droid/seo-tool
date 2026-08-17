import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { Reveal } from './premium/Reveal'

export default function PricingPlans({ pricing, onCta }) {
  if (!pricing?.plans?.length) return null

  return (
    <section className="wds-section wds-pricing" id="pricing" aria-label="Pricing">
      <div className="cz-rail">
        <Reveal className="wds-section-head">
          <p className="cz-kicker">{pricing.kicker}</p>
          <h2>{pricing.title}</h2>
          <p className="cz-whisper">{pricing.lead}</p>
        </Reveal>

        <div className="wds-pricing-grid">
          {pricing.plans.map((plan) => (
            <Reveal
              as="article"
              key={plan.name}
              className={`wds-price-card${plan.featured ? ' is-featured' : ''}`}
            >
              {plan.badge ? <p className="wds-price-badge">{plan.badge}</p> : null}
              <p className="wds-price-name">{plan.name}</p>
              <p className="wds-price-amount">
                <span>{plan.price}</span>
                <small>{plan.period}</small>
              </p>
              <p className="wds-price-copy">{plan.copy}</p>
              <ul>
                {plan.features.map((feature) => (
                  <li key={feature}>
                    <CheckCircle2 size={16} strokeWidth={2.2} />
                    {feature}
                  </li>
                ))}
              </ul>
              <button type="button" className={plan.featured ? 'cz-btn-solid' : 'wds-price-ghost'} onClick={onCta}>
                {plan.cta}
                <ArrowRight size={16} strokeWidth={2.4} />
              </button>
            </Reveal>
          ))}
        </div>

        {pricing.note ? <p className="wds-pricing-note">{pricing.note}</p> : null}
      </div>
    </section>
  )
}
