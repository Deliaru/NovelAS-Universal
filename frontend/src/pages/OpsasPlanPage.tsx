import { useCallback, useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import Editor from '@toast-ui/editor'
import '@toast-ui/editor/dist/toastui-editor.css'
import {
  listOpsasCategories,
  listOpsasPlans,
  readOpsasPlan,
  writeOpsasPlan,
  deleteOpsasPlan,
  createOpsasPlan,
} from '../api/client'
import { useProjectStore } from '../store/projectStore'

const AUTO_SAVE_DELAY_MS = 800

type SaveState = 'idle' | 'unsaved' | 'saving' | 'saved' | 'error'

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

interface CategoryInfo {
  category: string
  label: string
  count: number
}

interface PlanInfo {
  category: string
  category_label: string
  name: string
  path: string
  size: number
  mtime: number
}

interface PlanDetail {
  category: string
  name: string
  path: string
  content: string
}

export default function OpsasPlanPage() {
  const slug = useProjectStore((s) => s.currentSlug)
  const queryClient = useQueryClient()

  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
  const [draftContent, setDraftContent] = useState('')
  const [lastSavedContent, setLastSavedContent] = useState('')
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newCategory, setNewCategory] = useState<string>('song-release')

  const draftRef = useRef('')
  const lastSavedRef = useRef('')
  const saveInFlightRef = useRef(false)
  const queuedSaveRef = useRef<string | null>(null)
  const editorContainerRef = useRef<HTMLDivElement | null>(null)
  const editorRef = useRef<Editor | null>(null)

  const { data: categories = [] } = useQuery<CategoryInfo[]>({
    queryKey: ['opsas-categories'],
    queryFn: listOpsasCategories,
  })

  const { data: plans = [] } = useQuery<PlanInfo[]>({
    queryKey: ['opsas-plans', activeCategory],
    queryFn: () => listOpsasPlans(activeCategory ?? undefined),
  })

  const selected = selectedPath ? selectedPath.split('/') : null
  const selectedCategory = selected?.[0] ?? null
  const selectedName = selected?.[1] ?? null

  const { data: planDetail } = useQuery<PlanDetail>({
    queryKey: ['opsas-plan-detail', selectedCategory, selectedName],
    queryFn: () => readOpsasPlan(selectedCategory!, selectedName!),
    enabled: !!selectedCategory && !!selectedName,
  })

  const saveMutation = useMutation({
    mutationFn: (p: { category: string; name: string; content: string }) =>
      writeOpsasPlan(p.category, p.name, p.content),
  })

  const createMutation = useMutation({
    mutationFn: createOpsasPlan,
    onSuccess: (data: { category: string; name: string; path: string }) => {
      queryClient.invalidateQueries({ queryKey: ['opsas-plans'] })
      queryClient.invalidateQueries({ queryKey: ['opsas-categories'] })
      setSelectedPath(data.path)
      setActiveCategory(data.category)
      setShowCreate(false)
      setNewTitle('')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (p: { category: string; name: string }) => deleteOpsasPlan(p.category, p.name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opsas-plans'] })
      queryClient.invalidateQueries({ queryKey: ['opsas-categories'] })
      setSelectedPath(null)
    },
  })

  const saveNow = useCallback(
    async (content: string): Promise<boolean> => {
      if (!selectedCategory || !selectedName) return true
      if (saveInFlightRef.current) {
        queuedSaveRef.current = content
        return true
      }
      saveInFlightRef.current = true
      setSaveState('saving')
      setSaveError(null)
      try {
        await saveMutation.mutateAsync({
          category: selectedCategory,
          name: selectedName,
          content,
        })
        lastSavedRef.current = content
        setLastSavedContent(content)
        setSaveState('saved')
        queryClient.setQueryData<PlanDetail>(
          ['opsas-plan-detail', selectedCategory, selectedName],
          (old) => (old ? { ...old, content } : old)
        )
        return true
      } catch (error) {
        const message = error instanceof Error ? error.message : '保存失败'
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
    [selectedCategory, selectedName, queryClient, saveMutation]
  )

  const flushPendingSave = useCallback(async (): Promise<boolean> => {
    const timeoutAt = Date.now() + 5000
    while (saveInFlightRef.current && Date.now() < timeoutAt) {
      await sleep(50)
    }
    if (saveInFlightRef.current) {
      setSaveState('error')
      setSaveError('保存仍在进行中，请稍后重试')
      return false
    }
    if (draftRef.current === lastSavedRef.current) return true
    return saveNow(draftRef.current)
  }, [saveNow])

  useEffect(() => {
    if (!planDetail) {
      setDraftContent('')
      draftRef.current = ''
      setLastSavedContent('')
      lastSavedRef.current = ''
      setSaveState('idle')
      setSaveError(null)
      return
    }
    setDraftContent(planDetail.content)
    draftRef.current = planDetail.content
    setLastSavedContent(planDetail.content)
    lastSavedRef.current = planDetail.content
    setSaveState('idle')
    setSaveError(null)
    queuedSaveRef.current = null
  }, [planDetail])

  useEffect(() => {
    if (!planDetail || !editorContainerRef.current) return
    editorRef.current?.destroy()
    editorRef.current = new Editor({
      el: editorContainerRef.current,
      height: '100%',
      initialEditType: 'wysiwyg',
      initialValue: planDetail.content,
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
  }, [planDetail])

  useEffect(() => {
    if (!planDetail || draftContent === lastSavedContent) return
    setSaveState((prev) => (prev === 'saving' ? prev : 'unsaved'))
    const timer = window.setTimeout(() => {
      void saveNow(draftRef.current)
    }, AUTO_SAVE_DELAY_MS)
    return () => window.clearTimeout(timer)
  }, [planDetail, draftContent, lastSavedContent, saveNow])

  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      const hasUnsaved = draftRef.current !== lastSavedRef.current || saveInFlightRef.current
      if (!hasUnsaved) return
      event.preventDefault()
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [])

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

  const groupedPlans: Record<string, PlanInfo[]> = {}
  for (const plan of plans) {
    ;(groupedPlans[plan.category] ||= []).push(plan)
  }

  return (
    <div className="flex h-full gap-4 animate-fade-in">
      {/* Left: categories + plan list */}
      <div
        className="w-80 shrink-0 rounded-xl overflow-hidden shadow-sm flex flex-col"
        style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div className="p-4" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <h2
            className="text-lg font-bold mb-3 flex items-center gap-2"
            style={{ color: 'var(--color-text-primary)' }}
          >
            <span
              className="w-1.5 h-5 rounded-full"
              style={{ backgroundColor: 'var(--color-accent-primary)' }}
            ></span>
            运营计划 (OpsasPlan)
          </h2>
          <button
            onClick={() => setShowCreate(true)}
            className="w-full text-sm font-semibold rounded-lg px-3 py-2 transition-all duration-300"
            style={{
              backgroundColor: 'var(--color-accent-primary)',
              color: 'var(--color-bg-primary)',
            }}
          >
            + 新建计划
          </button>
        </div>

        <div className="p-2" style={{ borderBottom: '1px solid var(--color-border)' }}>
          <button
            className="w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-all"
            style={{
              backgroundColor: activeCategory === null ? 'var(--color-accent-light)' : 'transparent',
              color: activeCategory === null ? 'var(--color-accent-primary)' : 'var(--color-text-primary)',
            }}
            onClick={() => setActiveCategory(null)}
          >
            全部大类
          </button>
          {categories.map((cat) => {
            const isActive = activeCategory === cat.category
            return (
              <button
                key={cat.category}
                className="w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-all flex justify-between items-center"
                style={{
                  backgroundColor: isActive ? 'var(--color-accent-light)' : 'transparent',
                  color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-primary)',
                }}
                onClick={() => setActiveCategory(cat.category)}
              >
                <span>{cat.label}</span>
                <span
                  className="text-xs px-1.5 py-0.5 rounded-full"
                  style={{
                    backgroundColor: 'var(--color-bg-tertiary)',
                    color: 'var(--color-text-secondary)',
                  }}
                >
                  {cat.count}
                </span>
              </button>
            )
          })}
        </div>

        <div className="p-2 flex-1 overflow-auto">
          {plans.length === 0 && (
            <div
              className="text-center py-6 text-sm"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              暂无计划文件
            </div>
          )}
          {Object.entries(groupedPlans).map(([cat, list]) => (
            <div key={cat} className="mb-3">
              <div
                className="text-xs font-semibold px-2 py-1 mb-1"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                {list[0]?.category_label ?? cat}
              </div>
              {list.map((plan) => {
                const isActive = selectedPath === plan.path
                return (
                  <button
                    key={plan.path}
                    className="w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-all border-l-4"
                    style={{
                      backgroundColor: isActive ? 'var(--color-accent-light)' : 'transparent',
                      color: isActive
                        ? 'var(--color-accent-primary)'
                        : 'var(--color-text-primary)',
                      borderLeftColor: isActive
                        ? 'var(--color-accent-primary)'
                        : 'transparent',
                    }}
                    onClick={async () => {
                      if (draftRef.current !== lastSavedRef.current) {
                        const success = await flushPendingSave()
                        if (!success) return
                      }
                      setSelectedPath(plan.path)
                    }}
                  >
                    <div className="font-medium truncate">{plan.name}</div>
                    <div
                      className="text-xs pt-0.5 opacity-80"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      {Math.round(plan.size / 1024)} KB
                    </div>
                  </button>
                )
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Right: editor */}
      <div
        className="flex-1 flex flex-col rounded-xl overflow-hidden shadow-sm"
        style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)',
        }}
      >
        {planDetail ? (
          <>
            <div
              className="p-5 flex items-center justify-between"
              style={{ borderBottom: '1px solid var(--color-border)' }}
            >
              <div className="flex items-center gap-3">
                <h1
                  className="text-xl font-black"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {planDetail.path}
                </h1>
                <span
                  className="text-xs font-bold px-2.5 py-1 rounded-full"
                  style={saveStatusStyle[saveState]}
                >
                  {saveStatusText[saveState]}
                </span>
              </div>
              <button
                onClick={() => {
                  if (!selectedCategory || !selectedName) return
                  if (confirm(`确认删除 ${planDetail.path}？`)) {
                    deleteMutation.mutate({ category: selectedCategory, name: selectedName })
                  }
                }}
                className="text-xs font-semibold px-3 py-1.5 rounded-lg transition-all"
                style={{
                  backgroundColor: '#fee2e2',
                  color: '#991b1b',
                }}
              >
                删除
              </button>
            </div>
            <div className="p-5 flex-1 flex flex-col overflow-auto">
              {saveError && (
                <p
                  className="text-sm mb-4 px-4 py-2 rounded font-medium"
                  style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}
                >
                  {saveError}
                </p>
              )}
              <div
                className="flex-1 rounded-lg overflow-hidden shadow-sm min-h-[500px]"
                style={{ border: '1px solid var(--color-border)' }}
              >
                <div ref={editorContainerRef} className="lore-editor h-full" />
              </div>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p
              className="opacity-70"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              请在左侧选择或新建一份运营计划。
            </p>
          </div>
        )}
      </div>

      {/* Create modal */}
      {showCreate && (
        <div
          className="fixed inset-0 flex items-center justify-center z-50"
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setShowCreate(false)}
        >
          <div
            className="w-[480px] rounded-xl p-6 shadow-lg"
            style={{
              backgroundColor: 'var(--color-bg-card)',
              border: '1px solid var(--color-border)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2
              className="text-lg font-bold mb-4"
              style={{ color: 'var(--color-text-primary)' }}
            >
              新建运营计划
            </h2>
            <div className="mb-4">
              <label
                className="block text-sm font-medium mb-2"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                大类
              </label>
              <select
                className="w-full text-sm rounded-lg px-3 py-2 outline-none"
                style={{
                  backgroundColor: 'var(--color-bg-tertiary)',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-primary)',
                }}
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
              >
                {categories.map((c) => (
                  <option key={c.category} value={c.category}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label
                className="block text-sm font-medium mb-2"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                标题
              </label>
              <input
                type="text"
                className="w-full text-sm rounded-lg px-3 py-2 outline-none"
                style={{
                  backgroundColor: 'var(--color-bg-tertiary)',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-primary)',
                }}
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="例：契约合唱单曲发布方案"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                className="px-4 py-2 text-sm rounded-lg"
                style={{
                  backgroundColor: 'var(--color-bg-tertiary)',
                  color: 'var(--color-text-primary)',
                }}
                onClick={() => setShowCreate(false)}
              >
                取消
              </button>
              <button
                className="px-4 py-2 text-sm font-semibold rounded-lg"
                style={{
                  backgroundColor: 'var(--color-accent-primary)',
                  color: 'var(--color-bg-primary)',
                }}
                disabled={!newTitle || createMutation.isPending}
                onClick={() =>
                  createMutation.mutate({
                    category: newCategory,
                    title: newTitle,
                    slug: slug ?? '',
                  })
                }
              >
                创建
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
