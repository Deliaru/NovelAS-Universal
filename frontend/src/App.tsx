import { Navigate, Route, Routes } from 'react-router-dom'
import MainLayout from './components/Layout/MainLayout'
import DashboardPage from './pages/DashboardPage'
import ChaptersPage from './pages/ChaptersPage'
import LorePage from './pages/LorePage'
import SettingsPage from './pages/SettingsPage'
import DraftsPage from './pages/DraftsPage'
import KnowledgePage from './pages/KnowledgePage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="chapters" element={<ChaptersPage />} />
        <Route path="drafts" element={<DraftsPage />} />
        <Route path="lore" element={<LorePage />} />
        <Route path="knowledge" element={<KnowledgePage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}

export default App
