import { useState, useEffect, useRef } from 'react'
import { Zap, CheckCircle, XCircle, Clock, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react'
import { getJobStatus } from '../api'

const STATUS_META = {
  pending:  { color: 'text-amber-400',  bg: 'bg-amber-400/10',  label: 'Pending' },
  running:  { color: 'text-sky-400',    bg: 'bg-sky-400/10',    label: 'Running' },
  done:     { color: 'text-emerald-400',bg: 'bg-emerald-400/10',label: 'Done' },
  partial:  { color: 'text-orange-400', bg: 'bg-orange-400/10', label: 'Partial' },
  failed:   { color: 'text-red-400',    bg: 'bg-red-400/10',    label: 'Failed' },
}

function JobCard({ jobId, onRemove }) {
  const [job, setJob] = useState(null)
  const [expanded, setExpanded] = useState(false)
  const intervalRef = useRef(null)

  const poll = async () => {
    try {
      const res = await getJobStatus(jobId)
      setJob(res.data)
      if (['done', 'partial', 'failed'].includes(res.data.status)) {
        clearInterval(intervalRef.current)
      }
    } catch (e) {
      clearInterval(intervalRef.current)
    }
  }

  useEffect(() => {
    poll()
    intervalRef.current = setInterval(poll, 2000)
    return () => clearInterval(intervalRef.current)
  }, [jobId])

  if (!job) return (
    <div className="card p-4 flex items-center gap-3 text-slate-500 text-sm">
      <RefreshCw size={14} className="animate-spin" /> Loading job {jobId.slice(0, 8)}...
    </div>
  )

  const meta = STATUS_META[job.status] || STATUS_META.pending
  const progress = job.total > 0 ? Math.round(((job.completed + job.failed) / job.total) * 100) : 0

  return (
    <div className="card">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${meta.color} ${meta.bg}`}>
            {meta.label}
            {job.status === 'running' && <RefreshCw size={10} className="inline ml-1 animate-spin" />}
          </span>
          <span className="text-xs text-slate-500 font-mono">{jobId.slice(0, 12)}...</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">{job.completed}/{job.total} done</span>
          {job.failed > 0 && <span className="text-xs text-red-400">{job.failed} failed</span>}
          <button onClick={() => setExpanded(e => !e)} className="text-slate-500 hover:text-slate-300 transition-colors">
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          <button onClick={() => onRemove(jobId)} className="text-slate-600 hover:text-red-400 transition-colors text-xs">✕</button>
        </div>
      </div>

      {/* Progress bar */}
      <div className="px-4 pb-3">
        <div className="w-full h-1.5 rounded-full bg-white/8 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${job.status === 'done' ? 'bg-emerald-500' : job.status === 'partial' ? 'bg-orange-500' : 'bg-indigo-500'}`}
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="text-[10px] text-slate-500 mt-1">{progress}% complete</div>
      </div>

      {/* Results */}
      {expanded && job.results.length > 0 && (
        <div className="border-t border-white/5 max-h-48 overflow-y-auto">
          {job.results.map((r, i) => (
            <div key={i} className="flex items-center gap-2 px-4 py-2 border-b border-white/3 last:border-0">
              {r.error
                ? <XCircle size={11} className="text-red-400 flex-shrink-0" />
                : <CheckCircle size={11} className="text-emerald-400 flex-shrink-0" />}
              <span className="text-xs text-slate-400 truncate">
                {r.error ? r.error : (r.city || r.title || JSON.stringify(r).slice(0, 60))}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function JobsPage() {
  const [jobIds, setJobIds] = useState(() => {
    try { return JSON.parse(localStorage.getItem('seo_jobs') || '[]') } catch { return [] }
  })
  const [newJobId, setNewJobId] = useState('')

  const saveJobs = (ids) => {
    setJobIds(ids)
    localStorage.setItem('seo_jobs', JSON.stringify(ids))
  }

  const addJob = () => {
    const id = newJobId.trim()
    if (id && !jobIds.includes(id)) {
      saveJobs([id, ...jobIds])
      setNewJobId('')
    }
  }

  const removeJob = (id) => saveJobs(jobIds.filter(j => j !== id))

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-xl font-bold text-white">Job Queue</h1>
        <p className="text-sm text-slate-500 mt-0.5">Track async bulk generation and publishing jobs</p>
      </div>

      <div className="card p-4">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Track a Job</div>
        <div className="flex gap-2">
          <input
            value={newJobId}
            onChange={e => setNewJobId(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addJob()}
            placeholder="Paste job ID from bulk generate/publish..."
            className="flex-1 bg-white/4 border border-white/8 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
          />
          <button onClick={addJob} className="btn-primary px-4 py-2 rounded-lg text-white text-sm font-semibold">
            Track
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          Job IDs are returned when you start a bulk generate or publish job from the Content or WordPress pages.
        </p>
      </div>

      {jobIds.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-16 text-slate-500">
          <Zap size={32} className="mb-3 opacity-30" />
          <p className="text-sm">No jobs tracked yet. Start a bulk operation to see jobs here.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobIds.map(id => (
            <JobCard key={id} jobId={id} onRemove={removeJob} />
          ))}
        </div>
      )}
    </div>
  )
}
