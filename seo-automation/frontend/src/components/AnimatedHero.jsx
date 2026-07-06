import { useState, useEffect } from 'react'
import { ArrowRight, Sparkles, Zap } from 'lucide-react'

export default function AnimatedHero() {
  const [displayText, setDisplayText] = useState('')
  const fullText = 'Enterprise-Grade AI SEO Automation'
  
  useEffect(() => {
    let index = 0
    const interval = setInterval(() => {
      if (index < fullText.length) {
        setDisplayText(fullText.substring(0, index + 1))
        index++
      } else {
        clearInterval(interval)
      }
    }, 50)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 overflow-hidden flex items-center justify-center">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-500/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-500/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      {/* Grid background */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(139,92,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(139,92,246,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      {/* Content */}
      <div className="relative z-10 max-w-4xl mx-auto px-8 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-full mb-8 animate-fade-in">
          <Sparkles className="w-4 h-4 text-purple-300" />
          <span className="text-sm font-semibold text-purple-200">Now with Real-Time Streaming & Multi-Model AI</span>
        </div>

        {/* Main heading with typing effect */}
        <h1 className="text-6xl md:text-7xl font-black mb-6 leading-tight">
          <span className="bg-gradient-to-r from-white via-purple-50 to-white bg-clip-text text-transparent">
            {displayText}
            <span className="animate-pulse">▌</span>
          </span>
        </h1>

        {/* Subheading */}
        <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">
          Generate SEO-optimized content, analyze competitors, and automate your entire workflow with cutting-edge AI technology
        </p>

        {/* Features list */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          {[
            { icon: '⚡', text: 'Real-Time Streaming' },
            { icon: '🧠', text: 'Multi-Model AI' },
            { icon: '🔍', text: 'Semantic Search' },
          ].map((feature, i) => (
            <div
              key={i}
              className="p-4 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 rounded-xl hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <span className="text-2xl mb-2 block">{feature.icon}</span>
              <p className="text-sm font-semibold text-slate-300">{feature.text}</p>
            </div>
          ))}
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <button className="group px-8 py-4 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 text-white font-bold rounded-xl hover:shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 flex items-center justify-center gap-2">
            <Zap className="w-5 h-5" />
            Get Started
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          <button className="px-8 py-4 bg-slate-800/50 border border-purple-500/30 text-white font-bold rounded-xl hover:border-purple-500/50 hover:bg-slate-800/80 transition-all duration-300">
            View Demo
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 pt-12 border-t border-purple-500/20">
          {[
            { number: '99.9%', label: 'Uptime' },
            { number: '2.1s', label: 'Avg Latency' },
            { number: '94.2%', label: 'Accuracy' },
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <p className="text-3xl md:text-4xl font-black bg-gradient-to-r from-purple-200 to-pink-200 bg-clip-text text-transparent mb-2">
                {stat.number}
              </p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Floating elements */}
      <div className="absolute top-20 left-10 w-20 h-20 bg-purple-500/10 rounded-full blur-2xl animate-float" />
      <div className="absolute bottom-20 right-10 w-32 h-32 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
    </div>
  )
}
