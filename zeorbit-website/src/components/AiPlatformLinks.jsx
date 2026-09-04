import { useMemo } from 'react'
import { useLocation } from 'react-router-dom'
import { AI_PLATFORMS, ASK_AI_ICON_SRC, askAiHref } from '../data/aiPlatforms'

export default function AiPlatformLinks() {
  const { pathname } = useLocation()
  const meta = useMemo(() => {
    const url =
      typeof window !== 'undefined'
        ? `https://zeorbit.com${pathname === '/' ? '/' : pathname}`
        : 'https://zeorbit.com/'
    const title = typeof document !== 'undefined' ? document.title : ''
    return { url, title }
  }, [pathname])

  return (
    <div className="zo-host-footer-ai" role="group" aria-label="Ask AI about this ZeOrbit page">
      {AI_PLATFORMS.map((p) => {
        const local = ASK_AI_ICON_SRC[p.icon]
        return (
          <a
            key={p.name}
            href={askAiHref(p, meta)}
            target="_blank"
            rel="nofollow noopener noreferrer"
            aria-label={`Ask ${p.name} about this page`}
            title={p.name}
            className="zo-host-ai-link"
            style={{ background: p.color }}
          >
            <img
              src={local || `https://cdn.simpleicons.org/${p.icon}/ffffff`}
              alt=""
              width="18"
              height="18"
            />
          </a>
        )
      })}
    </div>
  )
}
