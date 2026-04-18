import { NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listProjects } from '../../api/client'
import { useProjectStore } from '../../store/projectStore'
import type { ProjectSummary } from '../../types'

const navItems = [
  { to: '/dashboard', label: '工作台' },
  { to: '/chapters', label: '章节' },
  { to: '/chapter-outlines', label: '章纲' },
  { to: '/drafts', label: '草稿箱' },
  { to: '/lore', label: '设定库' },
  { to: '/knowledge', label: '大纲库' },
  { to: '/opsas-plan', label: '运营计划' },
  { to: '/settings', label: '设置' },
]

export default function Sidebar() {
  const { currentSlug, setCurrentSlug } = useProjectStore()
  const { data: projects = [] } = useQuery<ProjectSummary[]>({
    queryKey: ['projects'],
    queryFn: listProjects,
  })

  return (
    <aside className="w-64 flex flex-col transition-all duration-300" style={{
      backgroundColor: 'var(--color-bg-secondary)',
      borderRight: '1px solid var(--color-border)'
    }}>
      {/* Header */}
      <div className="p-4 flex items-center gap-2" style={{ borderBottom: '1px solid var(--color-border)' }}>
        <h1 className="text-xl font-black tracking-tight drop-shadow-sm transition-transform duration-300 hover:scale-105" style={{ color: 'var(--color-accent-primary)' }}>NovelAS</h1>
        <span className="px-1.5 py-0.5 rounded text-[10px] font-bold tracking-wider" style={{
          backgroundColor: 'var(--color-accent-primary)',
          color: 'var(--color-bg-primary)'
        }}>PRO</span>
      </div>

      {/* Project selector */}
      <div className="p-4" style={{ borderBottom: '1px solid var(--color-border)' }}>
        <div className="text-xs font-semibold mb-2" style={{ color: 'var(--color-text-tertiary)' }}>选择项目</div>
        <select
          className="w-full text-sm rounded-lg px-3 py-2 transition-all duration-300 transform outline-none focus:ring-2"
          style={{
            backgroundColor: 'var(--color-bg-tertiary)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-primary)'
          }}
          value={currentSlug || ''}
          onChange={(e) => setCurrentSlug(e.target.value || null)}
        >
          <option value="">-- 请选择项目 --</option>
          {projects.map((p) => (
            <option key={p.slug} value={p.slug}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `block px-4 py-2.5 rounded-lg text-sm transition-all duration-300 ${
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
