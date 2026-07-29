import { Search, Target, TrendingUp, Users, Link2, MapPin, Sparkles, FileBarChart } from 'lucide-react'

const FEATURES = [
  { icon: Target,      title: 'Site Audit',            desc: 'Crawl every page and surface technical, on-page, and performance issues with clear fixes.' },
  { icon: Search,      title: 'Keyword Research',       desc: 'Find profitable keywords with real volume, difficulty, CPC, and intent data.' },
  { icon: TrendingUp,  title: 'Rank Tracking',          desc: 'Track daily rankings by location and device, down to the city level.' },
  { icon: Users,       title: 'Competitor Analysis',    desc: 'See exactly which keywords and pages are driving your competitors’ traffic.' },
  { icon: Link2,       title: 'Backlink Analysis',      desc: 'Monitor your backlink profile and discover new link opportunities.' },
  { icon: MapPin,      title: 'Local SEO',              desc: 'Manage your Google Business Profile and track map-pack rankings by city.' },
  { icon: Sparkles,    title: 'AI Search Visibility',   desc: 'See how your brand shows up in Google AI Overviews, ChatGPT, and Perplexity.' },
  { icon: FileBarChart,title: 'SEO Reports',            desc: 'Generate polished, white-label client reports in one click.' },
]

export default function FeatureGrid() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {FEATURES.map(f => (
        <div key={f.title} className="card card-hover" style={{ padding: 22 }}>
          <div style={{ width: 40, height: 40, borderRadius: 11, background: 'var(--brand-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
            <f.icon size={19} style={{ color: 'var(--brand)' }} />
          </div>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-1)', margin: '0 0 6px' }}>{f.title}</h3>
          <p style={{ fontSize: 13, color: 'var(--text-3)', lineHeight: 1.6, margin: 0 }}>{f.desc}</p>
        </div>
      ))}
    </div>
  )
}
