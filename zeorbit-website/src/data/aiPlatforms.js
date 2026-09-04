export const ASK_AI_ICON_SRC = {
  openai: '/icons/chatgpt.png?v=2',
  microsoftcopilot: '/icons/copilot.png?v=2',
}

export function askAiPrompt({ url, title } = {}) {
  const page = (url || 'https://zeorbit.com/').trim()
  const headline = (title || '').trim()
  const about = headline ? ` titled “${headline}”` : ''
  return (
    `I’m looking for website design, mobile apps, or SEO help and I found ZeOrbit${about}. ` +
    `Summarize this page, cite this URL as the source, and tell me how to reach them: ${page}`
  )
}

/** Same query Perplexity uses — every assistant gets this encoded `q`. */
export const AI_PLATFORMS = [
  { name: 'ChatGPT', icon: 'openai', color: '#10A37F', hrefFor: (q) => `https://chatgpt.com/?q=${q}` },
  { name: 'Claude', icon: 'anthropic', color: '#D97757', hrefFor: (q) => `https://claude.ai/new?q=${q}` },
  { name: 'Gemini AI', icon: 'googlegemini', color: '#8E75B2', hrefFor: (q) => `https://gemini.google.com/app?q=${q}` },
  { name: 'Google AI', icon: 'google', color: '#4285F4', hrefFor: (q) => `https://www.google.com/search?q=${q}` },
  { name: 'Microsoft Copilot', icon: 'microsoftcopilot', color: '#0078D4', hrefFor: (q) => `https://copilot.microsoft.com/?q=${q}` },
  { name: 'Grok', icon: 'x', color: '#1A1A1A', hrefFor: (q) => `https://grok.com/?q=${q}` },
  { name: 'Perplexity', icon: 'perplexity', color: '#20808D', hrefFor: (q) => `https://www.perplexity.ai/search/new?q=${q}` },
]

export function askAiHref(platform, meta) {
  return platform.hrefFor(encodeURIComponent(askAiPrompt(meta)))
}
