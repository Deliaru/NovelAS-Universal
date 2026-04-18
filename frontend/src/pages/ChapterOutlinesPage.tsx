import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import Editor from '@toast-ui/editor'
import '@toast-ui/editor/dist/toastui-editor.css'
import { useProjectStore } from '../store/projectStore'
import { listChapterOutlines, readChapterOutlineFile, saveChapterOutlineFile } from '../api/client'
import type {
  ChapterWorkspaceFileContent,
  ChapterWorkspaceFileItem,
  ChapterWorkspaceFileKey,
  ChapterWorkspaceListItem,
} from '../types'

const AUTO_SAVE_DELAY_MS = 800
const FILE_TABS: Array<{ key: Extract<ChapterWorkspaceFileKey, 'outline' | 'concept'>; label: string }> = [
  { key: 'outline', label: '章纲' },
  { key: 'concept', label: '构思' },
]

type SaveState = 'idle' | 'unsaved' | 'saving' | 'saved' | 'error'

type SelectedChapter = {
  type: string
  number: number
  volume: number
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

function getFileStatus(files: ChapterWorkspaceFileItem[], key: 'outline' | 'concept') {
  return files.find((file) => file.key === key)
}

export default function ChapterOutlinesPage() {
  const slug = useProjectStore((s) => s.currentSlug)
  const queryClient = useQueryClient()
  const [selectedVolume, setSelectedVolume] = useState<number>(1)
  const [selectedChapter, setSelectedChapter] = useState<SelectedChapter | null>(null)
  const [selectedFileKey, setSelectedFileKey] = useState<'outline' | 'concept'>('outline')
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

  const { data: workspaces = [] } = useQuery<ChapterWorkspaceListItem[]>({
    queryKey: ['chapter-outlines', slug, selectedVolume],
    queryFn: () => listChapterOutlines(slug!, selectedVolume),
    enabled: !!slug,
  })

  const selectedWorkspace = useMemo(
    () => workspaces.find((item) =>
      item.type === selectedChapter?.type &&
      item.number === selectedChapter?.number &&
      item.volume === selectedChapter?.volume
    ) ?? null,
    [selectedChapter, workspaces]
  )

  const availableTabs = useMemo(
    () => FILE_TABS.filter((tab) => getFileStatus(selectedWorkspace?.files ?? [], tab.key)?.exists),
    [selectedWorkspace]
  )

  const { data: fileDetail } = useQuery<ChapterWorkspaceFileContent>({
    queryKey: ['chapter-outline-detail', slug, selectedWorkspace, selectedFileKey],
    queryFn: () => readChapterOutlineFile(
      slug!,
      selectedWorkspace!.type,
      selectedWorkspace!.number,
      selectedWorkspace!.volume,
      selectedFileKey,
    ),
    enabled: !!slug && !!selectedWorkspace,
    retry: false,
  })

  const saveMutation = useMutation({
    mutationFn: (payload: {
      slug: string
      type: string
      number: number
      volume: number
      fileKey: 'outline' | 'concept'
      content: string
    }) => saveChapterOutlineFile(payload.slug, payload.type, payload.number, payload.volume, payload.fileKey, payload.content),
  })

  const saveNow = useCallback(async (content: string): Promise<boolean> => {
    if (!slug || !selectedChapter || !selectedWorkspace) {
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
        type: selectedChapter.type,
        number: selectedChapter.number,
        volume: selectedChapter.volume,
        fileKey: selectedFileKey,
        content,
      })

      lastSavedRef.current = content
      setLastSavedContent(content)
      setSaveState('saved')

      queryClient.setQueryData<ChapterWorkspaceFileContent>(
        ['chapter-outline-detail', slug, selectedWorkspace, selectedFileKey],
        (old) => old ? { ...old, content, exists: true, word_count: content.length } : old,
      )
      queryClient.invalidateQueries({ queryKey: ['chapter-outlines', slug, selectedVolume] })
      return true
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to save outline changes'
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
  }, [queryClient, saveMutation, selectedChapter, selectedFileKey, selectedVolume, selectedWorkspace, slug])

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
    if (!selectedWorkspace) {
      return
    }

    const preferredKey = selectedWorkspace.files.find((file) => file.key === 'outline' && file.exists)
      ? 'outline'
      : 'concept'
    setSelectedFileKey(preferredKey)
  }, [selectedWorkspace?.type, selectedWorkspace?.number, selectedWorkspace?.volume])

  useEffect(() => {
    if (availableTabs.length === 0) {
      return
    }

    if (!availableTabs.some((tab) => tab.key === selectedFileKey)) {
      setSelectedFileKey(availableTabs[0].key)
    }
  }, [availableTabs, selectedFileKey])

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
  }, [draftContent, fileDetail, lastSavedContent, saveNow])

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

  const grouped = workspaces.reduce((acc, item) => {
    const key = item.type === 'Extra' ? '番外' : `第 ${item.volume} 卷`
    if (!acc[key]) acc[key] = []
    acc[key].push(item)
    return acc
  }, {} as Record<string, ChapterWorkspaceListItem[]>)

  const saveStatusText: Record<SaveState, string> = {
    idle: '内容无修改',
    unsaved: '有未保存的修改',
    saving: '保存中...',
    saved: '已保存',
    error: '保存失败',
  }

  const saveStatusStyle: Record<SaveState, CSSProperties> = {
    idle: { backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' },
    unsaved: { backgroundColor: '#fef3c7', color: '#b45309' },
    saving: { backgroundColor: 'var(--color-accent-light)', color: 'var(--color-accent-primary)' },
    saved: { backgroundColor: '#d1fae5', color: '#065f46' },
    error: { backgroundColor: '#fee2e2', color: '#991b1b' },
  }

  if (!slug) {
    return <div style={{ color: 'var(--color-text-secondary)' }}>请先在工作台选择一个项目。</div>
  }

  return (
    <div className="flex h-full gap-4 animate-fade-in">
      <div className="w-80 shrink-0 rounded-xl overflow-auto shadow-sm flex flex-col" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
      }}>
        <div className="p-4" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <h2 className="text-lg font-bold mb-3 flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
            <span className="w-1.5 h-5 rounded-full" style={{ backgroundColor: 'var(--color-accent-primary)' }}></span>
            章纲
          </h2>
          <div className="flex gap-1 mt-2">
            {[1, 2, 3].map((v) => (
              <button
                key={v}
                className="px-2 py-1 text-xs rounded transition-all duration-300"
                style={{
                  backgroundColor: selectedVolume === v ? 'var(--color-accent-primary)' : 'var(--color-bg-tertiary)',
                  color: selectedVolume === v ? 'var(--color-bg-primary)' : 'var(--color-text-secondary)',
                }}
                onClick={() => setSelectedVolume(v)}
              >
                卷 {v}
              </button>
            ))}
            <button
              className="px-2 py-1 text-xs rounded transition-all duration-300"
              style={{
                backgroundColor: selectedVolume === 0 ? 'var(--color-accent-primary)' : 'var(--color-bg-tertiary)',
                color: selectedVolume === 0 ? 'var(--color-bg-primary)' : 'var(--color-text-secondary)',
              }}
              onClick={() => setSelectedVolume(0)}
            >
              番外
            </button>
          </div>
        </div>

        <div className="p-2 flex-1 overflow-auto">
          {Object.keys(grouped).length === 0 && (
            <div className="text-center py-6 text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
              当前卷暂无章纲工作区
            </div>
          )}
          {Object.entries(grouped).map(([group, items]) => (
            <div key={group} className="mb-3">
              <p className="text-xs font-medium px-2 mb-1" style={{ color: 'var(--color-text-tertiary)' }}>{group}</p>
              {items.map((item) => {
                const isActive = selectedChapter?.type === item.type &&
                  selectedChapter?.number === item.number &&
                  selectedChapter?.volume === item.volume
                const outlineFile = getFileStatus(item.files, 'outline')
                const conceptFile = getFileStatus(item.files, 'concept')
                const draftFile = item.files.find((file) => file.key === 'draft')

                return (
                  <button
                    key={`${item.type}-${item.volume}-${item.number}`}
                    className="w-full text-left px-3 py-2.5 rounded-lg text-sm mb-1.5 transition-all duration-300 border-l-4"
                    style={{
                      backgroundColor: isActive ? 'var(--color-accent-light)' : 'transparent',
                      color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-primary)',
                      borderLeftColor: isActive ? 'var(--color-accent-primary)' : 'transparent',
                    }}
                    onClick={async () => {
                      if (draftRef.current !== lastSavedRef.current) {
                        const success = await flushPendingSave()
                        if (!success) {
                          return
                        }
                      }
                      setSelectedChapter({ type: item.type, number: item.number, volume: item.volume })
                    }}
                  >
                    <div className="font-bold">{item.display_name}</div>
                    <div className="text-xs pt-1 flex gap-1 flex-wrap" style={{ color: 'var(--color-text-secondary)' }}>
                      <span>{outlineFile?.exists ? '章纲' : '无章纲'}</span>
                      <span>{conceptFile?.exists ? '构思' : '无构思'}</span>
                      <span>{draftFile?.exists ? '有草稿' : '无草稿'}</span>
                    </div>
                  </button>
                )
              })}
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col rounded-xl overflow-hidden shadow-sm" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
      }}>
        {selectedWorkspace && fileDetail ? (
          <>
            <div className="p-5 flex items-center justify-between" style={{ borderBottom: '1px solid var(--color-border)' }}>
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="text-2xl font-black" style={{ color: 'var(--color-text-primary)' }}>{selectedWorkspace.display_name}</h1>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={saveStatusStyle[saveState]}>
                  {saveStatusText[saveState]}
                </span>
                {availableTabs.length > 0 ? (
                  <div className="flex gap-2">
                    {availableTabs.map((tab) => {
                      const isActive = selectedFileKey === tab.key
                      return (
                        <button
                          key={tab.key}
                          className="px-3 py-1.5 text-sm rounded-md transition-all duration-300"
                          style={{
                            backgroundColor: isActive ? 'var(--color-accent-primary)' : 'var(--color-bg-tertiary)',
                            color: isActive ? 'var(--color-bg-primary)' : 'var(--color-text-secondary)',
                          }}
                          onClick={async () => {
                            if (draftRef.current !== lastSavedRef.current) {
                              const success = await flushPendingSave()
                              if (!success) {
                                return
                              }
                            }
                            setSelectedFileKey(tab.key)
                          }}
                        >
                          {tab.label}
                        </button>
                      )
                    })}
                  </div>
                ) : (
                  <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>该章节暂无可编辑章纲文件</span>
                )}
              </div>
            </div>

            <div className="p-5 flex-1 flex flex-col overflow-auto">
              {saveError && <p className="text-sm mb-4 px-4 py-2 rounded font-medium" style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}>{saveError}</p>}
              <section className="flex flex-col flex-1 h-full min-h-[500px]">
                <h2 className="text-sm font-bold mb-3 flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
                  <span className="w-1.5 h-4 rounded-full" style={{ backgroundColor: 'var(--color-accent-primary)' }}></span>
                  {selectedFileKey === 'outline' ? '章纲编辑' : '构思编辑'}（自动保存）
                </h2>
                <div className="flex-1 rounded-lg overflow-hidden shadow-sm" style={{ border: '1px solid var(--color-border)' }}>
                  <div ref={editorContainerRef} className="lore-editor h-full" />
                </div>
              </section>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="opacity-70" style={{ color: 'var(--color-text-tertiary)' }}>请在左侧选择一个已有章纲工作区的章节。</p>
          </div>
        )}
      </div>
    </div>
  )
}
