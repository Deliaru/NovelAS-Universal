import { NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listProjects } from '../../api/client'
import { useProjectStore } from '../../store/projectStore'
import type { ProjectSummary } from '../../types'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/chapters', label: 'Chapters' },
  { to: '/lore', label: 'Lore Database' },
  { to: '/settings', label: 'Settings' },
]

export default function Sidebar() {
  const { currentSlug, setCurrentSlug } = useProjectStore()
  const { data: projects = [] } = useQuery<ProjectSummary[]>({
    queryKey: ['projects'],
    queryFn: listProjects,
  })

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-lg font-bold text-gray-900">NovelAS</h1>
        <p className="text-xs text-gray-500">Universal</p>
      </div>

      {/* Project selector */}
      <div className="p-3 border-b border-gray-200">
        <select
          className="w-full text-sm border border-gray-300 rounded px-2 py-1.5 bg-white"
          value={currentSlug || ''}
          onChange={(e) => setCurrentSlug(e.target.value || null)}
        >
          <option value="">Select project...</option>
          {projects.map((p) => (
            <option key={p.slug} value={p.slug}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `block px-3 py-2 rounded text-sm mb-1 ${
                isActive
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 text-xs text-gray-400">
        v0.1.0
      </div>
    </aside>
  )
}
