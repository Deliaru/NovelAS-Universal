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
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Welcome to NovelAS Universal</h2>
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
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Chapters" value={chapters.length} />
        <StatCard label="Total Words" value={totalWords.toLocaleString()} />
        <StatCard label="Lore Entries" value={loreSnapshot?.total || 0} />
        <StatCard label="Plot Memories" value={memoryData?.count || 0} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Chapters by type */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-semibold mb-3">Chapters by Type</h3>
          {Object.entries(chaptersByType).map(([type, count]) => (
            <div key={type} className="flex justify-between py-1 text-sm">
              <span className="text-gray-600">{type}</span>
              <span className="font-medium">{count}</span>
            </div>
          ))}
        </div>

        {/* Lore by category */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-semibold mb-3">Lore by Category</h3>
          {Object.entries(loreCounts).map(([cat, count]) => (
            <div key={cat} className="flex justify-between py-1 text-sm">
              <span className="text-gray-600">{cat}</span>
              <span className="font-medium">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}
