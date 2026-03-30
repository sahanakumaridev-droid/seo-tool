import { useState } from 'react'
import { ChevronDown, ChevronUp, RefreshCw, Save, MapPin, CheckCircle } from 'lucide-react'
import { generateSingle, savePage } from '../api'

function ScoreRing({ score }) {
  const r = 22
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  const color = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'
  return (
    <div className="relative w-12 h-12 flex-shrink-0">
      <svg className="w-12 h-12 -rotate-90" viewBox="0 0 56 56">
        <circle cx="28" cy="28" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="4" />
        <circle cx="28" cy="28" r={r} fill="none" stroke={color} strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1s ease-out' }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-bold text-white">{score}</span>
      </div>
    </div>
  )
}

function ScoreBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-500">{label}</span>
        <span className="text-gray-300 font-medium">{value}%</span>
      </div>
      <div className="h-1 rounded-full bg-white/5 overflow-hidden">
        <div className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-700`} style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

export default function SEOCard({ block, businessType, index, onRegenerate }) {
  const [expanded, setExpanded] = useState(false)
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [activeTab, setActiveTab] = useState('content')

  const score = Math.round(block.readability_score || 75)

  const handleRegenerate = async () => {
    setLoading(true)
    try {
      const res = await generateSingle(businessType, block.city, block.state)
      onRegenerate?.(res.data)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    await savePage(businessType, block.city, block.state)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div
      className={`glass rounded-2xl overflow-hidden transition-all duration-300 animate-fade-up
        ${expanded ? 'border-indigo-500/30' : 'border-white/5 hover:border-white/10'}
        border`}
      style={{ animationDelay: `${Math.min(index * 40, 400)}ms`, animationFillMode: 'both', opacity: 0 }}
    >
      {/* Card header */}
      <div className="flex items-center gap-4 p-4">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border border-indigo-500/20 flex items-center justify-center flex-shrink-0">
          <MapPin size={14} className="text-indigo-400" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-white text-sm">{block.city}, {block.state}</h3>
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/20">
              {businessType}
            </span>
          </div>
          <p className="text-xs text-gray-500 truncate mt-0.5">{block.title}</p>
        </div>

        <div className="flex items-center gap-3">
          <ScoreRing score={score} />

          <div className="flex items-center gap-1.5">
            <button
              onClick={handleRegenerate}
              disabled={loading}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all disabled:opacity-50"
              title="Regenerate"
            >
              <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            </button>
            <button
              onClick={handleSave}
              className={`p-2 rounded-lg transition-all ${saved ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white'}`}
              title="Save"
            >
              {saved ? <CheckCircle size={13} /> : <Save size={13} />}
            </button>
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all"
            >
              {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            </button>
          </div>
        </div>
      </div>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-white/5">
          {/* Tabs */}
          <div className="flex gap-1 p-3 border-b border-white/5">
            {['content', 'keywords', 'faqs', 'schema'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all
                  ${activeTab === tab
                    ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                    : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'}`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="p-5">
            {activeTab === 'content' && (
              <div className="space-y-4">
                <Field label="SEO Title" value={block.title} />
                <Field label="Meta Description" value={block.meta_description} />
                <Field label="H1" value={block.h1} />
                <div>
                  <Label>H2 Headings</Label>
                  <ul className="mt-2 space-y-1.5">
                    {block.h2s.map((h, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                        <span className="text-indigo-500 mt-0.5 flex-shrink-0">H2</span>
                        {h}
                      </li>
                    ))}
                  </ul>
                </div>
                <Field label="Content" value={block.content} multiline />
                <Field label="Call to Action" value={block.cta} />
                <div className="grid grid-cols-3 gap-3 pt-2">
                  <ScoreBar label="Readability" value={score} color="from-indigo-500 to-violet-500" />
                  <ScoreBar label="Keyword Density" value={Math.round((block.keyword_density || 1.5) * 20)} color="from-sky-500 to-indigo-500" />
                  <ScoreBar label="Meta Complete" value={100} color="from-emerald-500 to-sky-500" />
                </div>
              </div>
            )}

            {activeTab === 'keywords' && (
              <div className="space-y-4">
                <div>
                  <Label>Primary Keyword</Label>
                  <span className="inline-block mt-2 px-3 py-1.5 rounded-lg bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 text-sm font-medium">
                    {block.keywords.primary}
                  </span>
                </div>
                <div>
                  <Label>Secondary Keywords</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {block.keywords.secondary.map((k, i) => (
                      <Chip key={i} label={k} color="violet" />
                    ))}
                  </div>
                </div>
                <div>
                  <Label>Long-tail Keywords</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {block.keywords.long_tail.map((k, i) => (
                      <Chip key={i} label={k} color="sky" />
                    ))}
                  </div>
                </div>
                <div>
                  <Label>"Near Me" Variations</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {block.keywords.near_me.map((k, i) => (
                      <Chip key={i} label={k} color="emerald" />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'faqs' && (
              <div className="space-y-3">
                {block.faqs.map((faq, i) => (
                  <div key={i} className="rounded-xl bg-white/3 border border-white/5 p-4">
                    <p className="text-sm font-semibold text-indigo-300 mb-2">{faq.question}</p>
                    <p className="text-sm text-gray-400 leading-relaxed">{faq.answer}</p>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'schema' && (
              <div>
                <Label>JSON-LD Schema Markup</Label>
                <pre className="mt-3 rounded-xl p-4 text-xs text-emerald-400 overflow-auto max-h-64 border leading-relaxed"
                  style={{ background: 'var(--bg-primary)', borderColor: 'var(--border)' }}>
                  {JSON.stringify(block.schema_markup, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function Field({ label, value, multiline }) {
  return (
    <div>
      <Label>{label}</Label>
      <p className={`mt-1.5 text-sm text-gray-300 leading-relaxed ${multiline ? 'whitespace-pre-line' : ''}`}>{value}</p>
    </div>
  )
}

function Label({ children }) {
  return <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{children}</span>
}

function Chip({ label, color }) {
  const colors = {
    indigo: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/25',
    violet: 'bg-violet-500/15 text-violet-300 border-violet-500/25',
    sky: 'bg-sky-500/15 text-sky-300 border-sky-500/25',
    emerald: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
  }
  return (
    <span className={`text-xs px-2.5 py-1 rounded-lg border ${colors[color]}`}>{label}</span>
  )
}
