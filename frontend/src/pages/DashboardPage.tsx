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
          <h2 className="text-2xl font-black mb-4 tracking-wide" style={{ color: 'var(--color-text-primary)' }}>欢迎使用 NovelAS Universal</h2>
          <p className="text-lg opacity-80">请在左侧边栏选择一个项目以开始创作。</p>
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

  const translateType = (type: string) => {
    const map: Record<string, string> = {
      'Chapter': '正文',
      'Prologue': '序章',
      'Interlude': '幕间',
      'Finale': '终章',
      'Extra': '番外'
    }
    return map[type] || type
  }

  const translateLoreCategory = (cat: string) => {
    const map: Record<string, string> = {
      'characters': '角色',
      'factions': '势力',
      'items': '物品',
      'locations': '地点',
      'worldview': '世界观'
    }
    return map[cat.toLowerCase()] || cat
  }

  return (
    <div className="animate-fade-in-up">
      <h1 className="text-3xl font-black mb-8 tracking-tight" style={{ color: 'var(--color-text-primary)' }}>工作台</h1>

      <div className="grid grid-cols-4 gap-6 mb-10">
        <StatCard label="总章节数" value={chapters.length} />
        <StatCard label="总字数" value={totalWords.toLocaleString()} />
        <StatCard label="设定条目" value={loreSnapshot?.total || 0} />
        <StatCard label="情节记忆" value={memoryData?.count || 0} />
      </div>

      <div className="grid grid-cols-2 gap-8">
        {/* Chapters by type */}
        <div className="rounded-xl p-6 transition-transform duration-300 transform-gpu hover:scale-[1.02] shadow-sm hover:shadow-md" style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)'
        }}>
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
            <span className="w-1.5 h-5 rounded-full" style={{ backgroundColor: 'var(--color-accent-primary)' }}></span>
            章节统计
          </h3>
          <div className="space-y-3">
            {Object.entries(chaptersByType).map(([type, count]) => (
              <div key={type} className="flex justify-between items-center py-2 px-3 rounded-lg transition-colors hover:bg-black/5 dark:hover:bg-white/5">
                <span className="font-medium" style={{ color: 'var(--color-text-secondary)' }}>{translateType(type)}</span>
                <span className="font-bold text-lg" style={{ color: 'var(--color-accent-primary)' }}>{count}</span>
              </div>
            ))}
            {Object.keys(chaptersByType).length === 0 && (
               <div className="text-center py-4" style={{ color: 'var(--color-text-tertiary)' }}>暂无章节数据</div>
            )}
          </div>
        </div>

        {/* Lore by category */}
        <div className="rounded-xl p-6 transition-transform duration-300 transform-gpu hover:scale-[1.02] shadow-sm hover:shadow-md" style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)'
        }}>
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
             <span className="w-1.5 h-5 rounded-full" style={{ backgroundColor: 'var(--color-accent-secondary, #10b981)' }}></span>
             设定库分类
          </h3>
          <div className="space-y-3">
            {Object.entries(loreCounts).map(([cat, count]) => (
              <div key={cat} className="flex justify-between items-center py-2 px-3 rounded-lg transition-colors hover:bg-black/5 dark:hover:bg-white/5">
                <span className="font-medium capitalize" style={{ color: 'var(--color-text-secondary)' }}>{translateLoreCategory(cat)}</span>
                <span className="font-bold text-lg" style={{ color: 'var(--color-accent-secondary, #10b981)' }}>{count}</span>
              </div>
            ))}
            {Object.keys(loreCounts).length === 0 && (
               <div className="text-center py-4" style={{ color: 'var(--color-text-tertiary)' }}>暂无设定数据</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-xl p-6 transition-all duration-300 transform-gpu hover:-translate-y-1 shadow-sm hover:shadow-lg relative overflow-hidden group" style={{
      backgroundColor: 'var(--color-bg-card)',
      border: '1px solid var(--color-border)'
    }}>
      <div className="absolute top-0 right-0 w-24 h-24 bg-current opacity-5 rounded-bl-[100px] transition-transform duration-500 group-hover:scale-150" style={{ color: 'var(--color-accent-primary)' }}></div>
      <p className="text-sm font-medium relative z-10" style={{ color: 'var(--color-text-secondary)' }}>{label}</p>
      <p className="text-3xl font-black mt-2 tracking-tight relative z-10" style={{ color: 'var(--color-text-primary)' }}>{value}</p>
    </div>
  )
}
