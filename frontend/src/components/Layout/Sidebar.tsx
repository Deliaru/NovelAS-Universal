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
    <aside className="w-64 flex flex-col" style={{
      backgroundColor: 'var(--color-bg-secondary)',
      borderRight: '1px solid var(--color-border)'
    }}>
      {/* Header */}
      <div className="p-4" style={{ borderBottom: '1px solid var(--color-border)' }}>
        <h1 className="text-lg font-bold" style={{ color: 'var(--color-accent-primary)' }}>NovelAS</h1>
        <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>Universal</p>
      </div>

      {/* Project selector */}
      <div className="p-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
        <select
          className="w-full text-sm rounded px-2 py-1.5 transition-all duration-fast"
          style={{
            backgroundColor: 'var(--color-bg-tertiary)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-primary)'
          }}
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
              `block px-3 py-2 rounded text-sm mb-1 transition-all duration-fast ${
                isActive
                  ? 'font-medium'
                  : ''
              }`
            }
            style={({ isActive }) => ({
              backgroundColor: isActive ? 'var(--color-accent-primary)' : 'transparent',
              color: isActive ? 'var(--color-bg-primary)' : 'var(--color-text-secondary)',
            })}
            onMouseEnter={(e) => {
              const target = e.currentTarget;
              if (!target.classList.contains('active')) {
                target.style.backgroundColor = 'var(--color-bg-hover)';
                target.style.color = 'var(--color-text-primary)';
              }
            }}
            onMouseLeave={(e) => {
              const target = e.currentTarget;
              if (!target.classList.contains('active')) {
                target.style.backgroundColor = 'transparent';
                target.style.color = 'var(--color-text-secondary)';
              }
            }}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-3 text-xs" style={{
        borderTop: '1px solid var(--color-border)',
        color: 'var(--color-text-tertiary)'
      }}>
        v0.1.0
      </div>
    </aside>
  )
}
