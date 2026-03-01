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
    return <div className="text-gray-500">Select a project first.</div>
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
      <div className="w-72 shrink-0 bg-white rounded-lg border border-gray-200 overflow-auto">
        <div className="p-3 border-b border-gray-200">
          <h2 className="font-semibold">Chapters</h2>
          <div className="flex gap-1 mt-2">
            {[1, 2, 3].map((v) => (
              <button
                key={v}
                className={`px-2 py-1 text-xs rounded ${
                  selectedVolume === v
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
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
              <p className="text-xs font-medium text-gray-400 px-2 mb-1">{group}</p>
              {items.map((ch) => (
                <button
                  key={`${ch.type}-${ch.volume}-${ch.number}`}
                  className={`w-full text-left px-2 py-1.5 rounded text-sm ${
                    selectedChapter?.type === ch.type &&
                    selectedChapter?.number === ch.number &&
                    selectedChapter?.volume === ch.volume
                      ? 'bg-blue-50 text-blue-700'
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                  onClick={() =>
                    setSelectedChapter({
                      type: ch.type,
                      number: ch.number,
                      volume: ch.volume,
                    })
                  }
                >
                  <span>{ch.display_name}</span>
                  <span className="text-xs text-gray-400 ml-2">
                    {ch.word_count.toLocaleString()}
                  </span>
                </button>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Right: Content reader */}
      <div className="flex-1 bg-white rounded-lg border border-gray-200 overflow-auto p-6">
        {contentLoading && <p className="text-gray-400">Loading...</p>}
        {content && (
          <>
            <h1 className="text-xl font-bold mb-4">{content.display_name}</h1>
            <p className="text-sm text-gray-500 mb-4">
              {content.word_count.toLocaleString()} words
            </p>
            <div className="markdown-content prose max-w-none">
              <ReactMarkdown>{content.content}</ReactMarkdown>
            </div>
          </>
        )}
        {!content && !contentLoading && (
          <p className="text-gray-400">Select a chapter to read.</p>
        )}
      </div>
    </div>
  )
}
