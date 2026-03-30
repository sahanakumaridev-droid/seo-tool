import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import DashboardPage from './pages/DashboardPage'
import KeywordsPage from './pages/KeywordsPage'
import CompetitorsPage from './pages/CompetitorsPage'
import ContentPage from './pages/ContentPage'
import RankingsPage from './pages/RankingsPage'
import ReportsPage from './pages/ReportsPage'

export default function App() {
  return (
    <div className="flex bg-[#0B0F17] min-h-screen" style={{ color: 'var(--text-primary)' }}>
      <Sidebar />
      <div className="main-content flex-1 flex flex-col">
        <Topbar />
        <div className="flex-1 p-6 overflow-auto">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/keywords" element={<KeywordsPage />} />
            <Route path="/competitors" element={<CompetitorsPage />} />
            <Route path="/content" element={<ContentPage />} />
            <Route path="/rankings" element={<RankingsPage />} />
            <Route path="/reports" element={<ReportsPage />} />
          </Routes>
        </div>
      </div>
    </div>
  )
}
