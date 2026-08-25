export const OPEN_CHAT_EVENT = 'zeorbit:open-chat'

export function openSiteChat(detail = {}) {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(OPEN_CHAT_EVENT, { detail }))
}
