/** Footer links — each icon opens that AI tool’s landing page with the ZeOrbit prompt. */
const Q = 'ZeOrbit+-+Web+Designers+%26+Mobile+App+Developers.'

export const AI_PLATFORMS = [
  { name: 'ChatGPT', href: `https://chatgpt.com/?q=${Q}`, icon: 'openai', color: '#10A37F' },
  { name: 'Claude', href: `https://claude.ai/new?q=${Q}`, icon: 'anthropic', color: '#D97757' },
  { name: 'Gemini AI', href: `https://gemini.google.com/app?q=${Q}`, icon: 'googlegemini', color: '#8E75B2' },
  { name: 'Google AI', href: `https://www.google.com/search?q=${Q}`, icon: 'google', color: '#4285F4' },
  { name: 'Microsoft Copilot', href: `https://copilot.microsoft.com/?q=${Q}`, icon: 'microsoftcopilot', color: '#0078D4' },
  { name: 'Grok', href: `https://grok.com/?q=${Q}`, icon: 'x', color: '#1A1A1A' },
  { name: 'Perplexity', href: `https://www.perplexity.ai/search/new?q=${Q}`, icon: 'perplexity', color: '#20808D' },
]
