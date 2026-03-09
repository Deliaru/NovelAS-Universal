import { useQuery } from '@tanstack/react-query'
import { useProjectStore } from '../store/projectStore'
import { listChapters, getLoreSnapshot, getMemoryCount } from '../api/client'
import type { ChapterListItem, LoreSnapshot } from '../types'

export default function DashboardPage() {
  const slug = useProjectStore((s) => s.currentSlug)

  const { data: chapters = [] } = useQuery<ChapterListItem[]>({
    queryKey: ['chapters', slug],
    queryFn: () => listChapters(slug!),
    enabled: !!slug,
  })

  const { data: loreSnapshot } = useQuery<LoreSnapshot>({
    queryKey: ['lore-snapshot', slug],
    queryFn: () => getLoreSnapshot(slug!),
    enabled: !!slug,
  })

  const { data: memoryData } = useQuery({
    queryKey: ['memory-count', slug],
    queryFn: () => getMemoryCount(slug!),
    enabled: !!slug,
  })

  if (!slug) {
    return (
      <div className="flex items-center justify-center h-full" style={{ color: 'var(--color-text-secondary)' }}>
        <div className="text-center animate-fade-in-up">
          <h2 className="text-xl font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>Welcome to NovelAS Universal</h2>
          <p>Select a project from the sidebar to get started.</p>
        </div>
      </div>
    )
  }

  const totalWords = chapters.reduce((sum, c) => sum + c.word_count, 0)
  const chaptersByType = chapters.reduce((acc, c) => {
    acc[c.type] = (acc[c.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const loreCounts = loreSnapshot?.entries.reduce((acc, e) => {
    acc[e.category] = (acc[e.category] || 0) + 1
    return acc
  }, {} as Record<string, number>) || {}

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>Dashboard</h1>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Chapters" value={chapters.length} />
        <StatCard label="Total Words" value={totalWords.toLocaleString()} />
        <StatCard label="Lore Entries" value={loreSnapshot?.total || 0} />
        <StatCard label="Plot Memories" value={memoryData?.count || 0} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Chapters by type */}
        <div className="rounded-lg p-4 animate-fade-in" style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <h3 className="font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>Chapters by Type</h3>
          {Object.entries(chaptersByType).map(([type, count]) => (
            <div key={type} className="flex justify-between py-1 text-sm">
              <span style={{ color: 'var(--color-text-secondary)' }}>{type}</span>
              <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{count}</span>
            </div>
          ))}
        </div>

        {/* Lore by category */}
        <div className="rounded-lg p-4 animate-fade-in" style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <h3 className="font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>Lore by Category</h3>
          {Object.entries(loreCounts).map(([cat, count]) => (
            <div key={cat} className="flex justify-between py-1 text-sm">
              <span style={{ color: 'var(--color-text-secondary)' }}>{cat}</span>
              <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-lg p-4 transition-all duration-normal hover:scale-105 animate-fade-in" style={{
      backgroundColor: 'var(--color-bg-card)',
      border: '1px solid var(--color-border)',
      boxShadow: 'var(--shadow-sm)'
    }}>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{label}</p>
      <p className="text-2xl font-bold mt-1" style={{ color: 'var(--color-accent-primary)' }}>{value}</p>
    </div>
  )
}
