import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

/** FAQ list — all closed by default (no pre-opened panel). */
export default function FaqAccordion({ items }) {
  const [openIndex, setOpenIndex] = useState(-1)

  return (
    <div className="rv-faq-list">
      {items.map((item, i) => {
        const open = openIndex === i
        return (
          <div key={item.q} className={`rv-faq-item${open ? ' open' : ''}`}>
            <button
              type="button"
              className="rv-faq-question"
              aria-expanded={open}
              onClick={() => setOpenIndex(open ? -1 : i)}
            >
              {item.q}
              <ChevronDown size={18} />
            </button>
            {open ? <div className="rv-faq-answer">{item.a}</div> : null}
          </div>
        )
      })}
    </div>
  )
}
