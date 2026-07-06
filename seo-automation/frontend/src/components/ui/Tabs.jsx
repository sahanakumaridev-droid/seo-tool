import { useState } from 'react'

export function Tabs({ children, defaultValue }) {
  const [activeTab, setActiveTab] = useState(defaultValue)
  return (
    <div>
      {children}
    </div>
  )
}

export function TabsList({ children }) {
  return (
    <div className="flex gap-2 border-b border-slate-700">
      {children}
    </div>
  )
}

export function TabsTrigger({ value, children, onClick }) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 text-sm font-medium text-slate-400 hover:text-white transition-colors"
    >
      {children}
    </button>
  )
}

export function TabsContent({ children }) {
  return <div>{children}</div>
}
