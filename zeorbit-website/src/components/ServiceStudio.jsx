import {
  BadgeCheck,
  GitBranch,
  LineChart,
  PenTool,
  Rocket,
  Search,
  Server,
  Shield,
} from 'lucide-react'
import { Reveal } from './premium/Reveal'

const ICONS = {
  BadgeCheck,
  GitBranch,
  LineChart,
  PenTool,
  Rocket,
  Search,
  Server,
  Shield,
}

export default function ServiceStudio({ page }) {
  if (!page.deliverables && !page.stack && !page.unique && !page.manifesto) return null

  return (
    <>
      {page.manifesto ? (
        <section className="wds-manifesto" aria-label="Approach">
          <Reveal className="cz-rail wds-manifesto-inner">
            <h2>{page.manifesto.title}</h2>
            <p>{page.manifesto.line}</p>
          </Reveal>
        </section>
      ) : null}

      {page.deliverables ? (
        <section className="wds-board" aria-label={page.deliverables.title}>
          <div className="cz-rail">
            <Reveal className="wds-board-head">
              <p className="cz-kicker is-light">{page.deliverables.kicker}</p>
              <h2>{page.deliverables.title}</h2>
              <p>{page.deliverables.lead}</p>
            </Reveal>
            <div className="wds-board-grid">
              {page.deliverables.items.map((item) => {
                const Icon = ICONS[item.icon]
                return (
                  <article key={item.title} className="wds-board-card">
                    {Icon ? (
                      <span className="wds-board-icon" aria-hidden="true">
                        <Icon size={18} strokeWidth={1.8} />
                      </span>
                    ) : null}
                    <h3>{item.title}</h3>
                    <p>{item.copy}</p>
                  </article>
                )
              })}
            </div>
          </div>
        </section>
      ) : null}

      {page.stack ? (
        <section className="wds-stack" aria-label={page.stack.kicker}>
          <div className="cz-rail">
            <Reveal className="wds-board-head">
              <p className="cz-kicker is-light">{page.stack.kicker}</p>
              <p className="wds-stack-lead">{page.stack.lead}</p>
            </Reveal>
            <div className="wds-stack-grid">
              {page.stack.groups.map((group) => (
                <article key={group.title} className="wds-stack-group">
                  <h3>{group.title}</h3>
                  {group.lines.map((line) => (
                    <p key={line}>{line}</p>
                  ))}
                </article>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {page.unique ? (
        <section className="wds-unique" aria-label={page.unique.kicker}>
          <div className="cz-rail">
            <Reveal className="wds-section-head">
              <p className="cz-kicker">{page.unique.kicker}</p>
              <h2>{page.unique.title}</h2>
            </Reveal>
            <div className="wds-unique-grid">
              {page.unique.items.map((item) => (
                <article key={item.title} className="wds-unique-card">
                  <h3>{item.title}</h3>
                  <p>{item.copy}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      ) : null}
    </>
  )
}
