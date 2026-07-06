import { useState, useEffect } from 'react'
import { Activity, Cpu, Zap, TrendingUp, BarChart3, Gauge } from 'lucide-react'

export default function AIMetricsDashboard() {
  const [metrics, setMetrics] = useState({
    apiLatency: 45,
    aiAccuracy: 94.2,
    throughput: 1250,
    activeJobs: 12,
    cacheHitRate: 87.5,
    modelLoad: 62,
  })

  // Simulate real-time metric updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        apiLatency: Math.max(30, Math.min(100, prev.apiLatency + (Math.random() - 0.5) * 20)),
        aiAccuracy: Math.max(85, Math.min(99, prev.aiAccuracy + (Math.random() - 0.5) * 2)),
        throughput: Math.max(800, Math.min(2000, prev.throughput + (Math.random() - 0.5) * 200)),
        activeJobs: Math.max(5, Math.min(20, prev.activeJobs + Math.floor((Math.random() - 0.5) * 4))),
        cacheHitRate: Math.max(70, Math.min(95, prev.cacheHitRate + (Math.random() - 0.5) * 3)),
        modelLoad: Math.max(40, Math.min(90, prev.modelLoad + (Math.random() - 0.5) * 10)),
      }))
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const MetricCard = ({ icon: Icon, label, value, unit, color, trend }) => (
    <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 p-6 hover:border-purple-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/20">
      {/* Animated background gradient */}
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300 bg-gradient-to-br ${color}`} />
      
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${color} bg-opacity-20`}>
            <Icon className={`w-5 h-5 text-${color.split('-')[1]}-300`} />
          </div>
          <div className={`text-xs font-semibold px-2 py-1 rounded-full ${trend > 0 ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}%
          </div>
        </div>
        <p className="text-sm text-slate-400 font-medium mb-2">{label}</p>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-white">{value.toFixed(1)}</span>
          <span className="text-sm text-slate-500">{unit}</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-4 h-1 bg-slate-700/50 rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${color} transition-all duration-500`}
          style={{ width: `${Math.min(100, (value / 100) * 100)}%` }}
        />
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-purple-400" />
            Live AI Metrics
          </h2>
          <p className="text-sm text-slate-400 mt-1">Real-time performance monitoring</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-lg">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-sm font-semibold text-green-300">System Healthy</span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          icon={Zap}
          label="API Latency"
          value={metrics.apiLatency}
          unit="ms"
          color="from-blue-500 to-cyan-500"
          trend={-2.5}
        />
        <MetricCard
          icon={Cpu}
          label="AI Accuracy"
          value={metrics.aiAccuracy}
          unit="%"
          color="from-purple-500 to-pink-500"
          trend={1.2}
        />
        <MetricCard
          icon={TrendingUp}
          label="Throughput"
          value={metrics.throughput}
          unit="req/s"
          color="from-green-500 to-emerald-500"
          trend={3.1}
        />
        <MetricCard
          icon={Activity}
          label="Active Jobs"
          value={metrics.activeJobs}
          unit="jobs"
          color="from-orange-500 to-red-500"
          trend={0.8}
        />
        <MetricCard
          icon={BarChart3}
          label="Cache Hit Rate"
          value={metrics.cacheHitRate}
          unit="%"
          color="from-indigo-500 to-purple-500"
          trend={2.3}
        />
        <MetricCard
          icon={Gauge}
          label="Model Load"
          value={metrics.modelLoad}
          unit="%"
          color="from-yellow-500 to-orange-500"
          trend={-1.5}
        />
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 rounded-2xl">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Active Services</h3>
          <div className="space-y-3">
            {[
              { name: 'FastAPI Backend', status: 'healthy', uptime: '99.9%' },
              { name: 'Semantic Search', status: 'healthy', uptime: '99.8%' },
              { name: 'AI Models', status: 'healthy', uptime: '99.7%' },
              { name: 'Cache Layer', status: 'healthy', uptime: '100%' },
            ].map((service, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                <span className="text-sm text-slate-300">{service.name}</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <span className="text-xs text-slate-400">{service.uptime}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 rounded-2xl">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">AI Model Status</h3>
          <div className="space-y-3">
            {[
              { name: 'GPT-4', status: 'active', tokens: '2.4M' },
              { name: 'Claude 3', status: 'active', tokens: '1.8M' },
              { name: 'Embeddings', status: 'active', tokens: '890K' },
              { name: 'Cohere', status: 'standby', tokens: '0' },
            ].map((model, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                <span className="text-sm text-slate-300">{model.name}</span>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${model.status === 'active' ? 'bg-green-500' : 'bg-slate-500'}`} />
                  <span className="text-xs text-slate-400">{model.tokens}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
