import { useState } from 'react'
import PremiumHeader from '../components/PremiumHeader'
import AIMetricsDashboard from '../components/AIMetricsDashboard'
import AIContentGenerator from '../components/AIContentGenerator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/Tabs'
import { BarChart3, Zap, Brain, Settings } from 'lucide-react'

export default function PremiumDashboard() {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <PremiumHeader />

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-8 py-12">
          {/* Tabs */}
          <div className="mb-8 flex gap-4 border-b border-purple-500/20">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'generator', label: 'AI Generator', icon: Brain },
              { id: 'analytics', label: 'Analytics', icon: Zap },
              { id: 'settings', label: 'Settings', icon: Settings },
            ].map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 font-medium flex items-center gap-2 border-b-2 transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'border-purple-500 text-white'
                      : 'border-transparent text-slate-300 hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>

          {/* Tab Content */}
          <div className="space-y-8">
            {activeTab === 'overview' && (
              <div className="space-y-8">
                <AIMetricsDashboard />
                
                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    { title: 'Generate Content', desc: 'AI-powered content creation', icon: '✨', color: 'from-purple-500 to-pink-500' },
                    { title: 'Semantic Search', desc: 'Find similar content', icon: '🔍', color: 'from-blue-500 to-cyan-500' },
                    { title: 'Competitor Analysis', desc: 'Analyze competitors', icon: '📊', color: 'from-green-500 to-emerald-500' },
                    { title: 'SEO Recommendations', desc: 'Get AI suggestions', icon: '🎯', color: 'from-orange-500 to-red-500' },
                  ].map((action, i) => (
                    <button
                      key={i}
                      className={`group p-6 bg-gradient-to-br ${action.color} bg-opacity-10 border border-purple-500/20 rounded-xl hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20 text-left`}
                    >
                      <div className="text-3xl mb-3">{action.icon}</div>
                      <h3 className="font-semibold text-white mb-1">{action.title}</h3>
                      <p className="text-sm text-slate-400">{action.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'generator' && (
              <AIContentGenerator />
            )}

            {activeTab === 'analytics' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {[
                    { title: 'Content Performance', metric: '94.2%', change: '+12.5%' },
                    { title: 'Engagement Rate', metric: '87.3%', change: '+8.2%' },
                    { title: 'Conversion Rate', metric: '6.8%', change: '+2.1%' },
                    { title: 'Avg. Position', metric: '3.2', change: '-0.8' },
                  ].map((stat, i) => (
                    <div key={i} className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 rounded-xl">
                      <p className="text-sm text-slate-400 mb-2">{stat.title}</p>
                      <div className="flex items-end justify-between">
                        <div>
                          <p className="text-3xl font-bold text-white">{stat.metric}</p>
                          <p className="text-xs text-green-400 mt-1">{stat.change}</p>
                        </div>
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <div className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 rounded-xl">
                  <h3 className="text-lg font-semibold text-white mb-4">API Configuration</h3>
                  <div className="space-y-4">
                    {[
                      { label: 'OpenAI API Key', value: 'sk-••••••••••••••••' },
                      { label: 'Anthropic API Key', value: 'sk-ant-••••••••••••••••' },
                      { label: 'Pinecone API Key', value: 'pcn-••••••••••••••••' },
                    ].map((setting, i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                        <span className="text-sm text-slate-300">{setting.label}</span>
                        <span className="text-xs text-slate-500">{setting.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
