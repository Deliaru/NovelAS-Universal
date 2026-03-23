import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useProjectStore } from '../store/projectStore'
import { listDrafts, readDraft, saveDraft } from '../api/client'
import type { ChapterListItem, ChapterContent } from '../types'

export default function DraftsPage() {
  const queryClient = useQueryClient()
  const slug = useProjectStore((s) => s.currentSlug)
  const [selectedVolume, setSelectedVolume] = useState<number>(1)
  const [selectedChapter, setSelectedChapter] = useState<{
    type: string; number: number; volume: number
  } | null>(null)
  
  const [editContent, setEditContent] = useState<string>('')

  const { data: chapters = [] } = useQuery<ChapterListItem[]>({
    queryKey: ['drafts', slug, selectedVolume],
    queryFn: () => listDrafts(slug!, selectedVolume),
    enabled: !!slug,
  })

  const { data: content, isLoading: contentLoading } = useQuery<ChapterContent>({
    queryKey: ['draft-content', slug, selectedChapter],
    queryFn: () =>
      readDraft(slug!, selectedChapter!.type, selectedChapter!.number, selectedChapter!.volume),
    enabled: !!slug && !!selectedChapter,
  })

  useEffect(() => {
    if (content) {
      setEditContent(content.content)
    } else {
      setEditContent('')
    }
  }, [content])

  const saveMutation = useMutation({
    mutationFn: () => 
      saveDraft(slug!, selectedChapter!.type, selectedChapter!.number, selectedChapter!.volume, editContent),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drafts', slug, selectedVolume] })
      queryClient.invalidateQueries({ queryKey: ['draft-content', slug, selectedChapter] })
      alert('保存成功！')
    },
    onError: (err) => {
      alert('保存失败: ' + err)
    }
  })

  if (!slug) {
    return <div style={{ color: 'var(--color-text-secondary)' }}>请先选择一个项目。</div>
  }

  // Group chapters by type
  const grouped = chapters.reduce((acc, ch) => {
    const key = ch.type === 'Extra' ? '番外' : `第 ${ch.volume} 卷`
    if (!acc[key]) acc[key] = []
    acc[key].push(ch)
    return acc
  }, {} as Record<string, ChapterListItem[]>)

  return (
    <div className="flex h-full gap-4 animate-fade-in">
      {/* Left: Draft list */}
      <div className="w-72 shrink-0 rounded-lg overflow-auto transition-transform duration-300 transform-gpu hover:scale-[1.01]" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div className="p-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <h2 className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>草稿箱</h2>
          <div className="flex gap-1 mt-2">
            {[1, 2, 3].map((v) => (
              <button
                key={v}
                className={`px-2 py-1 text-xs rounded transition-all duration-300`}
                style={{
                  backgroundColor: selectedVolume === v ? 'var(--color-accent-primary)' : 'var(--color-bg-tertiary)',
                  color: selectedVolume === v ? 'var(--color-bg-primary)' : 'var(--color-text-secondary)'
                }}
                onMouseEnter={(e) => {
                  if (selectedVolume !== v) {
                    e.currentTarget.style.backgroundColor = 'var(--color-bg-hover)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedVolume !== v) {
                    e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
                  }
                }}
                onClick={() => setSelectedVolume(v)}
              >
                卷 {v}
              </button>
            ))}
          </div>
        </div>

        <div className="p-2">
          {Object.entries(grouped).map(([group, items]) => (
            <div key={group} className="mb-3">
              <p className="text-xs font-medium px-2 mb-1" style={{ color: 'var(--color-text-tertiary)' }}>{group}</p>
              {items.map((ch) => {
                const isActive = selectedChapter?.type === ch.type &&
                  selectedChapter?.number === ch.number &&
                  selectedChapter?.volume === ch.volume;
                return (
                  <button
                    key={`${ch.type}-${ch.volume}-${ch.number}`}
                    className={`w-full text-left px-2 py-1.5 rounded text-sm transition-all duration-300`}
                    style={{
                      backgroundColor: isActive ? 'var(--color-accent-light)' : 'transparent',
                      color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-primary)',
                      borderLeft: isActive ? '3px solid var(--color-accent-primary)' : '3px solid transparent'
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = 'var(--color-bg-hover)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                    onClick={() =>
                      setSelectedChapter({
                        type: ch.type,
                        number: ch.number,
                        volume: ch.volume,
                      })
                    }
                  >
                    <span>{ch.display_name}</span>
                    <span className="text-xs ml-2" style={{ color: 'var(--color-text-tertiary)' }}>
                      {ch.word_count.toLocaleString()} 字
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Right: Content editor */}
      <div className="flex-1 flex flex-col rounded-lg overflow-hidden transition-all duration-300 animate-slide-up" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div className="p-4 flex justify-between items-center" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <div>
            <h1 className="text-xl font-bold transition-colors duration-300" style={{ color: 'var(--color-text-primary)' }}>
              {content ? content.display_name : '未选择草稿'}
            </h1>
            {content && (
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                {content.word_count.toLocaleString()} 字
              </p>
            )}
          </div>
          {content && (
            <button
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              className="px-4 py-2 rounded text-sm font-medium transition-all duration-300 hover:scale-105 active:scale-95 shadow-md hover:shadow-lg"
              style={{
                backgroundColor: 'var(--color-accent-primary)',
                color: 'var(--color-bg-primary)',
                opacity: saveMutation.isPending ? 0.7 : 1
              }}
            >
              {saveMutation.isPending ? '保存中...' : '保存修改'}
            </button>
          )}
        </div>
        
        <div className="flex-1 p-4 overflow-auto">
          {contentLoading && <p className="animate-pulse" style={{ color: 'var(--color-text-tertiary)' }}>加载中...</p>}
          {content && (
            <textarea
              className="w-full h-full p-4 rounded outline-none resize-none transition-shadow duration-300 focus:shadow-inner"
              style={{
                backgroundColor: 'var(--color-bg-primary)',
                color: 'var(--color-text-primary)',
                border: '1px solid var(--color-border)',
                fontFamily: 'inherit'
              }}
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              placeholder="在此编辑草稿内容..."
            />
          )}
          {!content && !contentLoading && (
            <div className="h-full flex items-center justify-center">
              <p style={{ color: 'var(--color-text-tertiary)' }}>请在左侧选择要编辑的草稿。</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
