/** Semrush-style “Top Issues” product card under the hero. */
import { Zap } from 'lucide-react'

const ISSUES = [
  'Duplicate title tags',
  '4xx errors',
  'Broken internal links',
  'Missing alt attributes',
  'Slow LCP on mobile',
]

export default function HeroVisual() {
  return (
    <div className="rv-issues-card" aria-label="Top SEO issues preview">
      <h3>Top Issues</h3>
      <ul>
        {ISSUES.map((issue) => (
          <li key={issue}>
            <span className="rv-issue-left">
              <Zap size={16} fill="currentColor" />
              {issue}
            </span>
            <a href="/register" className="rv-issue-fix">How to fix</a>
          </li>
        ))}
      </ul>
    </div>
  )
}
