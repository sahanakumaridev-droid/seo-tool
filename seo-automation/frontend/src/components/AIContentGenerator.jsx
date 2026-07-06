import { useState } from 'react'
import { Sparkles, Zap, Copy, Check, Loader } from 'lucide-react'

export default function AIContentGenerator() {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState('')
  const [copied, setCopied] = useState(false)
  const [selectedModel, setSelectedModel] = useState('gpt-4')

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    
    setIsGenerating(true)
    setGeneratedContent('')
    
    // Simulate streaming response
    const mockContent = `# ${prompt}

## Introduction
This is a premium AI-generated content piece that demonstrates the power of our semantic search and multi-model AI integration. Our system analyzes your requirements and generates optimized content in real-time.

## Key Features
- **Real-time Streaming**: Watch content generate token by token
- **Multi-Model AI**: Automatic fallback between GPT-4, Claude, and Cohere
- **Semantic Optimization**: Content optimized for search intent
- **Enterprise Grade**: Production-ready with 99.9% uptime

## Implementation Details
Our advanced AI system uses:
1. Semantic embeddings for context understanding
2. Multi-model ensemble for better accuracy
3. Real-time streaming for instant feedback
4. Automatic quality scoring and optimization

## Conclusion
This demonstrates the cutting-edge capabilities of our 2026 AI-tech platform.`

    // Simulate streaming by adding characters one by one
    for (let i = 0; i < mockContent.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 5))
      setGeneratedContent(mockContent.substring(0, i + 1))
    }
    
    setIsGenerating(false)
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedContent)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-400" />
            AI Content Generator
          </h2>
          <p className="text-sm text-slate-400 mt-1">Real-time streaming with multi-model AI</p>
        </div>
      </div>

      {/* Model Selector */}
      <div className="flex gap-3">
        {[
          { id: 'gpt-4', name: 'GPT-4', icon: '🚀' },
          { id: 'claude', name: 'Claude 3', icon: '🧠' },
          { id: 'cohere', name: 'Cohere', icon: '⚡' },
        ].map(model => (
          <button
            key={model.id}
            onClick={() => setSelectedModel(model.id)}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 flex items-center gap-2 ${
              selectedModel === model.id
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/50'
                : 'bg-slate-800/50 text-slate-300 border border-slate-700/50 hover:border-purple-500/50'
            }`}
          >
            <span>{model.icon}</span>
            {model.name}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="space-y-3">
        <label className="block text-sm font-semibold text-slate-300">
          Content Prompt
        </label>
        <div className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the content you want to generate... (e.g., 'Write an SEO-optimized blog post about web design trends')"
            className="w-full h-32 px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all resize-none"
          />
          <div className="absolute bottom-3 right-3 text-xs text-slate-500">
            {prompt.length} / 500
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={isGenerating || !prompt.trim()}
        className="w-full py-3 px-4 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
      >
        {isGenerating ? (
          <>
            <Loader className="w-5 h-5 animate-spin" />
            Generating with {selectedModel.toUpperCase()}...
          </>
        ) : (
          <>
            <Zap className="w-5 h-5" />
            Generate Content
          </>
        )}
      </button>

      {/* Generated Content Display */}
      {generatedContent && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-semibold text-slate-300">
              Generated Content
            </label>
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-3 py-1 text-xs font-medium text-slate-300 hover:text-white bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 rounded-lg transition-all"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-400" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy
                </>
              )}
            </button>
          </div>
          <div className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/20 rounded-xl max-h-96 overflow-y-auto">
            <div className="prose prose-invert max-w-none text-sm text-slate-300 space-y-3">
              {generatedContent.split('\n').map((line, i) => {
                if (line.startsWith('# ')) {
                  return <h1 key={i} className="text-2xl font-bold text-white mt-4 mb-2">{line.substring(2)}</h1>
                }
                if (line.startsWith('## ')) {
                  return <h2 key={i} className="text-xl font-bold text-purple-300 mt-3 mb-2">{line.substring(3)}</h2>
                }
                if (line.startsWith('- ')) {
                  return <li key={i} className="ml-4 text-slate-300">{line.substring(2)}</li>
                }
                if (line.startsWith('1. ') || line.startsWith('2. ') || line.startsWith('3. ')) {
                  return <li key={i} className="ml-4 text-slate-300">{line.substring(3)}</li>
                }
                if (line.trim()) {
                  return <p key={i} className="text-slate-300">{line}</p>
                }
                return <div key={i} className="h-2" />
              })}
              {isGenerating && <span className="animate-pulse">▌</span>}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg">
              <p className="text-xs text-slate-500 mb-1">Words</p>
              <p className="text-lg font-bold text-white">{generatedContent.split(/\s+/).length}</p>
            </div>
            <div className="p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg">
              <p className="text-xs text-slate-500 mb-1">Characters</p>
              <p className="text-lg font-bold text-white">{generatedContent.length}</p>
            </div>
            <div className="p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg">
              <p className="text-xs text-slate-500 mb-1">Read Time</p>
              <p className="text-lg font-bold text-white">{Math.ceil(generatedContent.split(/\s+/).length / 200)}m</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
