import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function MainLayout() {
  return (
    <div className="flex h-screen" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 animate-fade-in">
        <Outlet />
      </main>
    </div>
  )
}
