export default function StatCard({ label, value, sub, delta, icon, accent = 'indigo' }) {
  const isUp = delta && delta.startsWith('+')
  const accentMap = {
    indigo: 'text-indigo-400 bg-indigo-500/10',
    violet: 'text-violet-400 bg-violet-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    sky: 'text-sky-400 bg-sky-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
  }
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</span>
        {icon && (
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${accentMap[accent]}`}>
            {icon}
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="flex items-center gap-2">
        {delta && (
          <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${isUp ? 'badge-up' : 'badge-down'}`}>
            {delta}
          </span>
        )}
        {sub && <span className="text-xs text-slate-500">{sub}</span>}
      </div>
    </div>
  )
}
