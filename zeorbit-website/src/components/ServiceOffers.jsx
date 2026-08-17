import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { Reveal } from './premium/Reveal'

export default function ServiceOffers({ items, onCta }) {
  return (
    <div className="wds-offers">
      {items.map((item, index) => (
        <section
          key={item.id}
          id={item.id}
          className={`wds-offer${index % 2 ? ' is-flip is-snow' : ''}`}
          aria-labelledby={`${item.id}-title`}
        >
          <div className="cz-rail wds-offer-grid">
            <Reveal className="wds-offer-copy" eager>
              <p className="cz-kicker">{item.kicker || item.title}</p>
              <h2 id={`${item.id}-title`}>{item.title}</h2>
              <p>{item.copy}</p>
              {item.points?.length ? (
                <ul className="wds-offer-points">
                  {item.points.map((point) => (
                    <li key={point}>
                      <CheckCircle2 size={16} strokeWidth={2.2} />
                      {point}
                    </li>
                  ))}
                </ul>
              ) : null}
              <button type="button" className="cz-btn-solid" onClick={onCta}>
                {item.cta}
                <ArrowRight size={16} strokeWidth={2.4} />
              </button>
            </Reveal>
            <Reveal className="wds-offer-media" eager>
              <img src={item.image} alt="" loading="lazy" decoding="async" />
            </Reveal>
          </div>
        </section>
      ))}
    </div>
  )
}
