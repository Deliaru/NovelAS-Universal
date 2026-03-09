import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { useProjectStore } from '../store/projectStore'
import { listChapters, readChapter } from '../api/client'
import type { ChapterListItem, ChapterContent } from '../types'

export default function ChaptersPage() {
  const slug = useProjectStore((s) => s.currentSlug)
  const [selectedVolume, setSelectedVolume] = useState<number>(1)
  const [selectedChapter, setSelectedChapter] = useState<{
    type: string; number: number; volume: number
  } | null>(null)

  const { data: chapters = [] } = useQuery<ChapterListItem[]>({
    queryKey: ['chapters', slug, selectedVolume],
    queryFn: () => listChapters(slug!, selectedVolume),
    enabled: !!slug,
  })

  const { data: content, isLoading: contentLoading } = useQuery<ChapterContent>({
    queryKey: ['chapter-content', slug, selectedChapter],
    queryFn: () =>
      readChapter(slug!, selectedChapter!.type, selectedChapter!.number, selectedChapter!.volume),
    enabled: !!slug && !!selectedChapter,
  })

  if (!slug) {
    return <div style={{ color: 'var(--color-text-secondary)' }}>Select a project first.</div>
  }

  // Group chapters by type
  const grouped = chapters.reduce((acc, ch) => {
    const key = ch.type === 'Extra' ? 'Extra' : `Vol.${ch.volume}`
    if (!acc[key]) acc[key] = []
    acc[key].push(ch)
    return acc
  }, {} as Record<string, ChapterListItem[]>)

  return (
    <div className="flex h-full gap-4">
      {/* Left: Chapter list */}
      <div className="w-72 shrink-0 rounded-lg overflow-auto animate-fade-in" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div className="p-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <h2 className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Chapters</h2>
          <div className="flex gap-1 mt-2">
            {[1, 2, 3].map((v) => (
              <button
                key={v}
                className={`px-2 py-1 text-xs rounded transition-all duration-fast`}
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
                Vol.{v}
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
                    className={`w-full text-left px-2 py-1.5 rounded text-sm transition-all duration-fast`}
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
                      {ch.word_count.toLocaleString()}
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Right: Content reader */}
      <div className="flex-1 rounded-lg overflow-auto p-6 animate-fade-in" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        {contentLoading && <p style={{ color: 'var(--color-text-tertiary)' }}>Loading...</p>}
        {content && (
          <>
            <h1 className="text-xl font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>{content.display_name}</h1>
            <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
              {content.word_count.toLocaleString()} words
            </p>
            <div className="markdown-content prose max-w-none">
              <ReactMarkdown>{content.content}</ReactMarkdown>
            </div>
          </>
        )}
        {!content && !contentLoading && (
          <p style={{ color: 'var(--color-text-tertiary)' }}>Select a chapter to read.</p>
        )}
      </div>
    </div>
  )
}
