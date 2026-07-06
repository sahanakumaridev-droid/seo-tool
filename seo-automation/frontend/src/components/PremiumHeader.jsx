import { Sparkles, Zap, Brain, TrendingUp } from 'lucide-react'

export default function PremiumHeader() {
  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 border-b border-purple-500/20">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative px-8 py-12">
        <div className="max-w-7xl mx-auto">
          {/* Main heading with gradient */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-5xl font-black bg-gradient-to-r from-white via-purple-100 to-white bg-clip-text text-transparent">
                SEO Automation AI
              </h1>
              <div className="ml-4 px-3 py-1 bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-full">
                <span className="text-xs font-semibold text-purple-200 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> v2.1.0
                </span>
              </div>
            </div>
            <p className="text-lg text-slate-300 max-w-2xl">
              Enterprise-grade AI-powered SEO automation with real-time streaming, semantic search, and multi-model AI integration
            </p>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { icon: Zap, label: 'Real-time Streaming', value: '100ms latency' },
              { icon: Brain, label: 'Multi-Model AI', value: 'GPT-4 + Claude' },
              { icon: TrendingUp, label: 'Semantic Search', value: 'Vector DB' },
              { icon: Sparkles, label: 'Production Ready', value: 'Enterprise' },
            ].map((stat, i) => (
              <div
                key={i}
                className="group p-4 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 rounded-xl hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg group-hover:from-purple-500/40 group-hover:to-pink-500/40 transition-all">
                    <stat.icon className="w-4 h-4 text-purple-300" />
                  </div>
                  <span className="text-xs text-slate-400 font-medium">{stat.label}</span>
                </div>
                <p className="text-sm font-semibold text-purple-200">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
