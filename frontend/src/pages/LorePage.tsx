import { useCallback, useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import Editor from '@toast-ui/editor'
import '@toast-ui/editor/dist/toastui-editor.css'
import { useProjectStore } from '../store/projectStore'
import { getLoreSnapshot, getLoreDetails, searchLore, updateLoreEntry, getIndexFiles } from '../api/client'
import type { LoreEntry, LoreEntryDetail, LoreSearchResult, LoreSnapshot } from '../types'

const CATEGORIES = ['characters', 'factions', 'worldview', 'items', 'index']
const AUTO_SAVE_DELAY_MS = 800

type SaveState = 'idle' | 'unsaved' | 'saving' | 'saved' | 'error'

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export default function LorePage() {
  const slug = useProjectStore((s) => s.currentSlug)
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedEntry, setSelectedEntry] = useState<string | null>(null)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [draftContent, setDraftContent] = useState('')
  const [lastSavedContent, setLastSavedContent] = useState('')
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [saveError, setSaveError] = useState<string | null>(null)

  const draftRef = useRef('')
  const lastSavedRef = useRef('')
  const saveInFlightRef = useRef(false)
  const queuedSaveRef = useRef<string | null>(null)
  const editorContainerRef = useRef<HTMLDivElement | null>(null)
  const editorRef = useRef<Editor | null>(null)

  const { data: snapshot } = useQuery<LoreSnapshot>({
    queryKey: ['lore-snapshot', slug],
    queryFn: () => getLoreSnapshot(slug!),
    enabled: !!slug,
  })

  const { data: indexFiles } = useQuery<LoreEntry[]>({
    queryKey: ['lore-index', slug],
    queryFn: () => getIndexFiles(slug!),
    enabled: !!slug,
  })

  const { data: entryDetails } = useQuery<LoreEntryDetail[]>({
    queryKey: ['lore-detail', slug, selectedEntry],
    queryFn: () => getLoreDetails(slug!, [selectedEntry!]),
    enabled: !!slug && !!selectedEntry,
  })

  const { data: searchResults } = useQuery<LoreSearchResult[]>({
    queryKey: ['lore-search', slug, searchKeyword],
    queryFn: () => searchLore(slug!, searchKeyword),
    enabled: !!slug && searchKeyword.length > 1,
  })

  const saveMutation = useMutation({
    mutationFn: (payload: {
      slug: string
      category: string
      name: string
      content: string
      metadata?: Record<string, any>
    }) =>
      updateLoreEntry(payload.slug, payload.category, payload.name, {
        content: payload.content,
        metadata: payload.metadata,
      }),
  })

  if (!slug) {
    return <div style={{ color: 'var(--color-text-secondary)' }}>Select a project first.</div>
  }

  const entries = snapshot?.entries || []
  const indexEntries = indexFiles || []
  const allEntries = [...entries, ...indexEntries]

  const filtered = selectedCategory
    ? allEntries.filter((e) => e.category === selectedCategory)
    : allEntries

  const detail = entryDetails?.[0]
  const displayEntries: Array<LoreEntry | LoreSearchResult> =
    searchKeyword.length > 1 ? searchResults || [] : filtered

  const saveNow = useCallback(
    async (content: string): Promise<boolean> => {
      if (!slug || !detail) {
        return true
      }

      if (saveInFlightRef.current) {
        queuedSaveRef.current = content
        return true
      }

      saveInFlightRef.current = true
      setSaveState('saving')
      setSaveError(null)

      try {
        await saveMutation.mutateAsync({
          slug,
          category: detail.category,
          name: detail.name,
          content,
          metadata: detail.metadata,
        })

        lastSavedRef.current = content
        setLastSavedContent(content)
        setSaveState('saved')

        queryClient.setQueryData<LoreEntryDetail[]>(['lore-detail', slug, selectedEntry], (old) => {
          if (!old || old.length === 0) {
            return old
          }
          return [{ ...old[0], content }]
        })

        queryClient.setQueryData<LoreSnapshot>(['lore-snapshot', slug], (old) => {
          if (!old) {
            return old
          }
          return {
            ...old,
            entries: old.entries.map((entry) =>
              entry.id === detail.id
                ? { ...entry, summary: content.replace(/\n/g, ' ').trim().slice(0, 150) }
                : entry
            ),
          }
        })

        return true
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Failed to save changes'
        setSaveState('error')
        setSaveError(message)
        return false
      } finally {
        saveInFlightRef.current = false
        const queuedContent = queuedSaveRef.current
        if (queuedContent !== null && queuedContent !== lastSavedRef.current) {
          queuedSaveRef.current = null
          void saveNow(queuedContent)
        }
      }
    },
    [detail, queryClient, saveMutation, selectedEntry, slug]
  )

  const flushPendingSave = useCallback(async (): Promise<boolean> => {
    const timeoutAt = Date.now() + 5000
    while (saveInFlightRef.current && Date.now() < timeoutAt) {
      await sleep(50)
    }

    if (saveInFlightRef.current) {
      setSaveState('error')
      setSaveError('A save is still in progress. Please try again.')
      return false
    }

    if (draftRef.current === lastSavedRef.current) {
      return true
    }

    return saveNow(draftRef.current)
  }, [saveNow])

  const handleSelectEntry = useCallback(
    async (entryId: string) => {
      if (entryId === selectedEntry) {
        return
      }

      const ok = await flushPendingSave()
      if (!ok) {
        window.alert('Failed to save the current lore changes. Please retry before switching entries.')
        return
      }

      setSelectedEntry(entryId)
    },
    [flushPendingSave, selectedEntry]
  )

  useEffect(() => {
    if (!detail) {
      setDraftContent('')
      draftRef.current = ''
      setLastSavedContent('')
      lastSavedRef.current = ''
      setSaveState('idle')
      setSaveError(null)
      return
    }

    setDraftContent(detail.content)
    draftRef.current = detail.content
    setLastSavedContent(detail.content)
    lastSavedRef.current = detail.content
    setSaveState('idle')
    setSaveError(null)
    queuedSaveRef.current = null
  }, [detail])

  useEffect(() => {
    if (!detail || !editorContainerRef.current) {
      return
    }

    editorRef.current?.destroy()
    editorRef.current = new Editor({
      el: editorContainerRef.current,
      height: '560px',
      initialEditType: 'wysiwyg',
      initialValue: detail.content,
      autofocus: false,
      usageStatistics: false,
      events: {
        change: () => {
          const markdown = editorRef.current?.getMarkdown() ?? ''
          setDraftContent(markdown)
          draftRef.current = markdown
          if (markdown !== lastSavedRef.current) {
            setSaveState((prev) => (prev === 'saving' ? prev : 'unsaved'))
          }
        },
      },
    })

    return () => {
      editorRef.current?.destroy()
      editorRef.current = null
    }
  }, [detail])

  useEffect(() => {
    if (!detail || draftContent === lastSavedContent) {
      return
    }

    setSaveState((prev) => (prev === 'saving' ? prev : 'unsaved'))
    const timer = window.setTimeout(() => {
      void saveNow(draftRef.current)
    }, AUTO_SAVE_DELAY_MS)

    return () => window.clearTimeout(timer)
  }, [detail, draftContent, lastSavedContent, saveNow])

  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      const hasUnsaved = draftRef.current !== lastSavedRef.current || saveInFlightRef.current
      if (!hasUnsaved) {
        return
      }
      event.preventDefault()
      event.returnValue = ''
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [])

  const saveStatusText: Record<SaveState, string> = {
    idle: 'No changes',
    unsaved: 'Unsaved changes',
    saving: 'Saving...',
    saved: 'Saved',
    error: 'Save failed',
  }

  const saveStatusClass: Record<SaveState, string> = {
    idle: '',
    unsaved: '',
    saving: '',
    saved: '',
    error: '',
  }

  const saveStatusStyle: Record<SaveState, React.CSSProperties> = {
    idle: { backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' },
    unsaved: { backgroundColor: '#fef3c7', color: '#b45309' },
    saving: { backgroundColor: 'var(--color-accent-light)', color: 'var(--color-accent-primary)' },
    saved: { backgroundColor: '#d1fae5', color: '#065f46' },
    error: { backgroundColor: '#fee2e2', color: '#991b1b' },
  }

  return (
    <div className="flex h-full gap-4">
      {/* Left: Entry list */}
      <div className="w-72 shrink-0 rounded-lg overflow-auto animate-fade-in" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div className="p-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <h2 className="font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>Lore Database</h2>
          <input
            type="text"
            placeholder="Search..."
            className="w-full text-sm rounded px-2 py-1 transition-all duration-fast"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-primary)'
            }}
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
          />
          <div className="flex flex-wrap gap-1 mt-2">
            <button
              className="px-2 py-0.5 text-xs rounded transition-all duration-fast"
              style={{
                backgroundColor: !selectedCategory ? 'var(--color-accent-primary)' : 'var(--color-bg-tertiary)',
                color: !selectedCategory ? 'var(--color-bg-primary)' : 'var(--color-text-secondary)'
              }}
              onClick={() => setSelectedCategory(null)}
            >
              All
            </button>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                className="px-2 py-0.5 text-xs rounded transition-all duration-fast"
                style={{
                  backgroundColor: selectedCategory === cat ? 'var(--color-accent-primary)' : 'var(--color-bg-tertiary)',
                  color: selectedCategory === cat ? 'var(--color-bg-primary)' : 'var(--color-text-secondary)'
                }}
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="p-2">
          {displayEntries.map((entry) => {
            const isActive = selectedEntry === entry.id;
            return (
              <button
                key={entry.id}
                className="w-full text-left px-2 py-2 rounded text-sm mb-1 transition-all duration-fast"
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
                onClick={async () => {
                  if (draftRef.current !== lastSavedRef.current) {
                    const success = await flushPendingSave()
                    if (!success) {
                      return
                    }
                  }
                  setSelectedEntry(entry.id)
                }}
              >
                <div className="font-medium">{entry.name}</div>
                <div className="text-xs mt-0.5" style={{ color: 'var(--color-text-tertiary)' }}>
                  {entry.category}
                  {'summary' in entry && entry.summary && ` • ${entry.summary.slice(0, 60)}...`}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Right: Entry detail */}
      <div className="flex-1 rounded-lg overflow-auto p-6 animate-fade-in" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        {detail ? (
          <>
            <div className="flex items-center gap-3 mb-3">
              <h1 className="text-xl font-bold" style={{ color: 'var(--color-text-primary)' }}>{detail.name}</h1>
              <span className="text-xs px-2 py-0.5 rounded" style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                color: 'var(--color-text-secondary)'
              }}>
                {detail.category}
              </span>
              <span className="text-xs px-2 py-0.5 rounded" style={saveStatusStyle[saveState]}>
                {saveStatusText[saveState]}
              </span>
            </div>
            {saveError && <p className="text-sm mb-3" style={{ color: '#dc2626' }}>{saveError}</p>}
            {detail.metadata && Object.keys(detail.metadata).length > 0 && (
              <div className="rounded p-3 mb-4 text-sm" style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                border: '1px solid var(--color-border)'
              }}>
                {Object.entries(detail.metadata).map(([k, v]) => (
                  <div key={k} className="flex gap-2">
                    <span className="min-w-[100px]" style={{ color: 'var(--color-text-secondary)' }}>{k}:</span>
                    <span style={{ color: 'var(--color-text-primary)' }}>{String(v)}</span>
                  </div>
                ))}
              </div>
            )}

            <section className="flex flex-col">
              <h2 className="text-sm font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>
                WYSIWYG Markdown Editor (auto-save)
              </h2>
              <div ref={editorContainerRef} className="lore-editor rounded" style={{ border: '1px solid var(--color-border)' }} />
            </section>
          </>
        ) : (
          <p style={{ color: 'var(--color-text-tertiary)' }}>Select a lore entry to view details.</p>
        )}
      </div>
    </div>
  )
}
