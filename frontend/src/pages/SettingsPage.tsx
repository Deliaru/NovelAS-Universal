import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useProjectStore } from '../store/projectStore'
import { getProject, createProject, convertDocx } from '../api/client'
import type { Project } from '../types'

export default function SettingsPage() {
  const slug = useProjectStore((s) => s.currentSlug)
  const setCurrentSlug = useProjectStore((s) => s.setCurrentSlug)
  const queryClient = useQueryClient()

  const { data: project } = useQuery<Project>({
    queryKey: ['project', slug],
    queryFn: () => getProject(slug!),
    enabled: !!slug,
  })

  // Create project form
  const [newName, setNewName] = useState('')
  const [newSlug, setNewSlug] = useState('')
  const [newDesc, setNewDesc] = useState('')

  const createMutation = useMutation({
    mutationFn: () =>
      createProject({
        name: newName,
        slug: newSlug,
        description: newDesc,
        volumes: [
          { number: 1, title: 'Volume 1', source_dir: 'source/vol1' },
        ],
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setCurrentSlug(data.slug)
      setNewName('')
      setNewSlug('')
      setNewDesc('')
    },
  })

  const convertMutation = useMutation({
    mutationFn: () => convertDocx(slug!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chapters', slug] })
    },
  })

  return (
    <div className="max-w-3xl mx-auto animate-fade-in-up">
      <h1 className="text-3xl font-black mb-8 tracking-tight" style={{ color: 'var(--color-text-primary)' }}>设置</h1>

      {/* Current project info */}
      {project && (
        <section className="rounded-xl p-6 mb-8 transition-all duration-300 transform-gpu hover:scale-[1.01] shadow-sm hover:shadow-md" style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)'
        }}>
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
            <span className="w-1.5 h-5 rounded-full" style={{ backgroundColor: 'var(--color-accent-primary)' }}></span>
            当前项目
          </h2>
          <div className="text-sm space-y-3 pl-3">
            <p className="flex justify-between max-w-sm"><span style={{ color: 'var(--color-text-secondary)' }}>项目名称:</span> <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{project?.name}</span></p>
            <p className="flex justify-between max-w-sm"><span style={{ color: 'var(--color-text-secondary)' }}>标识 (Slug):</span> <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{project?.slug}</span></p>
            <p className="flex justify-between max-w-sm"><span style={{ color: 'var(--color-text-secondary)' }}>卷数:</span> <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{project?.volumes?.length}</span></p>
            <p className="flex justify-between max-w-sm"><span style={{ color: 'var(--color-text-secondary)' }}>默认语言:</span> <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{project?.settings?.language}</span></p>
          </div>

          <div className="mt-6 pt-4" style={{ borderTop: '1px solid var(--color-border)' }}>
            <h3 className="text-sm font-bold mb-3" style={{ color: 'var(--color-text-primary)' }}>DOCX 转换</h3>
            <div className="flex items-center gap-4">
              <button
                className="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-300 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 shadow-sm"
                style={{
                  backgroundColor: convertMutation.isSuccess ? '#10b981' : 'var(--color-accent-primary)',
                  color: 'var(--color-bg-primary)'
                }}
                onClick={() => convertMutation.mutate()}
                disabled={convertMutation.isPending}
              >
                {convertMutation.isPending ? '转换中...' : '转换所有文档 (DOCX)'}
              </button>
              {convertMutation.data && (
                <p className="text-sm font-medium animate-fade-in" style={{ color: '#10b981' }}>
                  成功转换 {convertMutation.data.converted} 个文件
                </p>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Create new project */}
      <section className="rounded-xl p-6 transition-all duration-300 transform-gpu hover:scale-[1.01] shadow-sm hover:shadow-md" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)'
      }}>
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
          <span className="w-1.5 h-5 rounded-full" style={{ backgroundColor: 'var(--color-accent-secondary, #10b981)' }}></span>
          创建新项目
        </h2>
        <div className="space-y-4 max-w-xl">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>项目名称</label>
            <input
              type="text"
              className="w-full rounded-lg px-4 py-2 text-sm transition-all duration-300 outline-none focus:ring-2 shadow-inner"
              style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-primary)'
              }}
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="我的小说"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>项目标识 (英文/拼音)</label>
            <input
              type="text"
              className="w-full rounded-lg px-4 py-2 text-sm transition-all duration-300 outline-none focus:ring-2 shadow-inner"
              style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-primary)'
              }}
              value={newSlug}
              onChange={(e) => setNewSlug(e.target.value)}
              placeholder="my-novel"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>简介</label>
            <textarea
              className="w-full rounded-lg px-4 py-2 text-sm transition-all duration-300 outline-none focus:ring-2 shadow-inner resize-none"
              style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-primary)'
              }}
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              rows={3}
              placeholder="一段简短的介绍..."
            />
          </div>
          <button
            className="px-6 py-2.5 mt-2 font-medium text-sm rounded-lg transition-all duration-300 hover:scale-105 active:scale-95 shadow-md hover:shadow-lg disabled:opacity-50 disabled:hover:scale-100 disabled:shadow-sm"
            style={{
              backgroundColor: 'var(--color-accent-primary)',
              color: 'var(--color-bg-primary)'
            }}
            onClick={() => createMutation.mutate()}
            disabled={createMutation.isPending || !newName || !newSlug}
          >
            {createMutation.isPending ? '创建中...' : '创建新项目'}
          </button>
        </div>
      </section>
    </div>
  )
}
