import { useCallback, useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import Editor from '@toast-ui/editor'
import '@toast-ui/editor/dist/toastui-editor.css'
import { useProjectStore } from '../store/projectStore'
import { listProjectKnowledge, readKnowledge, updateKnowledge } from '../api/client'

const AUTO_SAVE_DELAY_MS = 800

type SaveState = 'idle' | 'unsaved' | 'saving' | 'saved' | 'error'

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

interface KnowledgeFile {
  path: string
  name: string
  size: number
}

export default function KnowledgePage() {
  const slug = useProjectStore((s) => s.currentSlug)
  const queryClient = useQueryClient()
  const [searchKeyword, setSearchKeyword] = useState('')
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
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

  const { data: knowledgeFiles } = useQuery<KnowledgeFile[]>({
    queryKey: ['knowledge-list', slug],
    queryFn: () => listProjectKnowledge(slug!),
    enabled: !!slug,
  })

  const { data: fileDetail } = useQuery<{ path: string; content: string }>({
    queryKey: ['knowledge-detail', slug, selectedPath],
    queryFn: () => readKnowledge(selectedPath!, slug!),
    enabled: !!slug && !!selectedPath,
  })

  const saveMutation = useMutation({
    mutationFn: (payload: { slug: string; path: string; content: string }) =>
      updateKnowledge(payload.path, payload.content, payload.slug),
  })

  // Basic cleanup and save functionality exactly alike LorePage
  const saveNow = useCallback(
    async (content: string): Promise<boolean> => {
      if (!slug || !selectedPath) {
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
          path: selectedPath,
          content,
        })

        lastSavedRef.current = content
        setLastSavedContent(content)
        setSaveState('saved')

        queryClient.setQueryData<{ path: string; content: string }>(['knowledge-detail', slug, selectedPath], (old) => {
          if (!old) return old
          return { ...old, content }
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
    [selectedPath, queryClient, saveMutation, slug]
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

  useEffect(() => {
    if (!fileDetail) {
      setDraftContent('')
      draftRef.current = ''
      setLastSavedContent('')
      lastSavedRef.current = ''
      setSaveState('idle')
      setSaveError(null)
      return
    }

    setDraftContent(fileDetail.content)
    draftRef.current = fileDetail.content
    setLastSavedContent(fileDetail.content)
    lastSavedRef.current = fileDetail.content
    setSaveState('idle')
    setSaveError(null)
    queuedSaveRef.current = null
  }, [fileDetail])

  useEffect(() => {
    if (!fileDetail || !editorContainerRef.current) {
      return
    }

    editorRef.current?.destroy()
    editorRef.current = new Editor({
      el: editorContainerRef.current,
      height: '100%',
      initialEditType: 'wysiwyg',
      initialValue: fileDetail.content,
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
  }, [fileDetail])

  useEffect(() => {
    if (!fileDetail || draftContent === lastSavedContent) {
      return
    }

    setSaveState((prev) => (prev === 'saving' ? prev : 'unsaved'))
    const timer = window.setTimeout(() => {
      void saveNow(draftRef.current)
    }, AUTO_SAVE_DELAY_MS)

    return () => window.clearTimeout(timer)
  }, [fileDetail, draftContent, lastSavedContent, saveNow])

  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      const hasUnsaved = draftRef.current !== lastSavedRef.current || saveInFlightRef.current
      if (!hasUnsaved) {
        return
      }
      event.preventDefault()
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [])

  if (!slug) {
    return <div style={{ color: 'var(--color-text-secondary)' }}>请先在工作台选择一个项目。</div>
  }

  const saveStatusText: Record<SaveState, string> = {
    idle: '内容无修改',
    unsaved: '有未保存的修改',
    saving: '保存中...',
    saved: '已保存',
    error: '保存失败',
  }

  const saveStatusStyle: Record<SaveState, React.CSSProperties> = {
    idle: { backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' },
    unsaved: { backgroundColor: '#fef3c7', color: '#b45309' },
    saving: { backgroundColor: 'var(--color-accent-light)', color: 'var(--color-accent-primary)' },
    saved: { backgroundColor: '#d1fae5', color: '#065f46' },
    error: { backgroundColor: '#fee2e2', color: '#991b1b' },
  }

  const files = knowledgeFiles || []
  const displayFiles = searchKeyword
    ? files.filter(f => f.name.toLowerCase().includes(searchKeyword.toLowerCase()) || f.path.toLowerCase().includes(searchKeyword.toLowerCase()))
    : files

  return (
    <div className="flex h-full gap-4 animate-fade-in">
      {/* Left: Files list */}
      <div className="w-80 shrink-0 rounded-xl overflow-auto transition-transform duration-300 transform-gpu hover:scale-[1.01] shadow-sm flex flex-col" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)'
      }}>
        <div className="p-4" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <h2 className="text-lg font-bold mb-3 flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
            <span className="w-1.5 h-5 rounded-full" style={{ backgroundColor: 'var(--color-accent-primary)' }}></span>
            大纲库 (Knowledge)
          </h2>
          <input
            type="text"
            placeholder="搜索文件..."
            className="w-full text-sm rounded-lg px-3 py-2 transition-all duration-300 outline-none focus:ring-2 shadow-inner"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-primary)'
            }}
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
          />
        </div>

        <div className="p-2 flex-1 overflow-auto">
          {displayFiles.length === 0 && (
            <div className="text-center py-6 text-sm" style={{ color: 'var(--color-text-tertiary)' }}>无大纲文件</div>
          )}
          {displayFiles.map((file) => {
            const isActive = selectedPath === file.path;
            return (
              <button
                key={file.path}
                className="w-full text-left px-3 py-2.5 rounded-lg text-sm mb-1.5 transition-all duration-300 border-l-4"
                style={{
                  backgroundColor: isActive ? 'var(--color-accent-light)' : 'transparent',
                  color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-primary)',
                  borderLeftColor: isActive ? 'var(--color-accent-primary)' : 'transparent'
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
                  setSelectedPath(file.path)
                }}
              >
                <div className="font-bold">{file.name}</div>
                <div className="text-xs pt-1 opacity-80" style={{ color: 'var(--color-text-secondary)' }}>
                  {file.path} ({Math.round(file.size / 1024)} KB)
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Right: File detail */}
      <div className="flex-1 flex flex-col rounded-xl overflow-hidden transition-all duration-300 animate-slide-up shadow-sm" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)'
      }}>
        {fileDetail ? (
          <>
            <div className="p-5 flex items-center justify-between" style={{ borderBottom: '1px solid var(--color-border)' }}>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-black" style={{ color: 'var(--color-text-primary)' }}>{fileDetail.path}</h1>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full transition-all duration-300" style={saveStatusStyle[saveState]}>
                  {saveStatusText[saveState]}
                </span>
              </div>
            </div>
            
            <div className="p-5 flex-1 flex flex-col overflow-auto">
              {saveError && <p className="text-sm mb-4 px-4 py-2 rounded font-medium" style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}>{saveError}</p>}

              <section className="flex flex-col flex-1 h-full min-h-[500px]">
                <h2 className="text-sm font-bold mb-3 flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
                  <span className="w-1.5 h-4 rounded-full" style={{ backgroundColor: 'var(--color-accent-primary)' }}></span>
                  大纲编辑 (自动保存)
                </h2>
                <div className="flex-1 rounded-lg overflow-hidden shadow-sm hover:shadow transition-shadow duration-300" style={{ border: '1px solid var(--color-border)' }}>
                  <div ref={editorContainerRef} className="lore-editor h-full" />
                </div>
              </section>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="opacity-70" style={{ color: 'var(--color-text-tertiary)' }}>请在左侧选择一个大纲文件以查看和编辑。</p>
          </div>
        )}
      </div>
    </div>
  )
}
