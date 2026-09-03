import { AI_PLATFORMS } from '../data/aiPlatforms'

const LOCAL_ICONS = {
  openai: '/icons/chatgpt.png?v=2',
  microsoftcopilot: '/icons/copilot.png?v=2',
}

export default function AiPlatformLinks() {
  return (
    <div className="zo-host-footer-ai" role="group" aria-label="Ask AI about ZeOrbit">
      {AI_PLATFORMS.map((p) => {
        const local = LOCAL_ICONS[p.icon]
        return (
          <a
            key={p.name}
            href={p.href}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`Open ${p.name}`}
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
