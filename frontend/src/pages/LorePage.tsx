import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { useProjectStore } from '../store/projectStore'
import { getLoreSnapshot, getLoreDetails, searchLore } from '../api/client'
import type { LoreSnapshot, LoreEntry } from '../types'

const CATEGORIES = ['characters', 'factions', 'worldview', 'items']

export default function LorePage() {
  const slug = useProjectStore((s) => s.currentSlug)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedEntry, setSelectedEntry] = useState<string | null>(null)
  const [searchKeyword, setSearchKeyword] = useState('')

  const { data: snapshot } = useQuery<LoreSnapshot>({
    queryKey: ['lore-snapshot', slug],
    queryFn: () => getLoreSnapshot(slug!),
    enabled: !!slug,
  })

  const { data: entryDetails } = useQuery({
    queryKey: ['lore-detail', slug, selectedEntry],
    queryFn: () => getLoreDetails(slug!, [selectedEntry!]),
    enabled: !!slug && !!selectedEntry,
  })

  const { data: searchResults } = useQuery({
    queryKey: ['lore-search', slug, searchKeyword],
    queryFn: () => searchLore(slug!, searchKeyword),
    enabled: !!slug && searchKeyword.length > 1,
  })

  if (!slug) {
    return <div className="text-gray-500">Select a project first.</div>
  }

  const entries = snapshot?.entries || []
  const filtered = selectedCategory
    ? entries.filter((e) => e.category === selectedCategory)
    : entries

  const detail = entryDetails?.[0]

  return (
    <div className="flex h-full gap-4">
      {/* Left: Entry list */}
      <div className="w-72 shrink-0 bg-white rounded-lg border border-gray-200 overflow-auto">
        <div className="p-3 border-b border-gray-200">
          <h2 className="font-semibold mb-2">Lore Database</h2>
          <input
            type="text"
            placeholder="Search..."
            className="w-full text-sm border border-gray-300 rounded px-2 py-1"
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
          />
          <div className="flex flex-wrap gap-1 mt-2">
            <button
              className={`px-2 py-0.5 text-xs rounded ${
                !selectedCategory ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
              }`}
              onClick={() => setSelectedCategory(null)}
            >
              All
            </button>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                className={`px-2 py-0.5 text-xs rounded ${
                  selectedCategory === cat
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600'
                }`}
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="p-2">
          {(searchKeyword.length > 1 ? searchResults || [] : filtered).map((entry: any) => (
            <button
              key={entry.id}
              className={`w-full text-left px-2 py-2 rounded text-sm mb-1 ${
                selectedEntry === entry.id
                  ? 'bg-blue-50 text-blue-700'
                  : 'hover:bg-gray-50 text-gray-700'
              }`}
              onClick={() => setSelectedEntry(entry.id)}
            >
              <span className="font-medium">{entry.name}</span>
              <span className="text-xs text-gray-400 ml-1">({entry.category})</span>
              {entry.summary && (
                <p className="text-xs text-gray-500 mt-0.5 truncate">{entry.summary}</p>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Right: Entry detail */}
      <div className="flex-1 bg-white rounded-lg border border-gray-200 overflow-auto p-6">
        {detail ? (
          <>
            <div className="flex items-center gap-3 mb-4">
              <h1 className="text-xl font-bold">{detail.name}</h1>
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                {detail.category}
              </span>
            </div>
            {detail.metadata && Object.keys(detail.metadata).length > 0 && (
              <div className="bg-gray-50 rounded p-3 mb-4 text-sm">
                {Object.entries(detail.metadata).map(([k, v]) => (
                  <div key={k} className="flex gap-2">
                    <span className="text-gray-500 min-w-[100px]">{k}:</span>
                    <span>{String(v)}</span>
                  </div>
                ))}
              </div>
            )}
            <div className="markdown-content prose max-w-none">
              <ReactMarkdown>{detail.content}</ReactMarkdown>
            </div>
          </>
        ) : (
          <p className="text-gray-400">Select a lore entry to view details.</p>
        )}
      </div>
    </div>
  )
}
