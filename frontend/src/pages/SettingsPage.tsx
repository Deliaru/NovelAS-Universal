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
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-6" style={{ color: 'var(--color-text-primary)' }}>Settings</h1>

      {/* Current project info */}
      {project && (
        <section className="rounded-lg p-4 mb-6 animate-fade-in" style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <h2 className="font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>Current Project</h2>
          <div className="text-sm space-y-1">
            <p><span style={{ color: 'var(--color-text-secondary)' }}>Name:</span> <span style={{ color: 'var(--color-text-primary)' }}>{project.name}</span></p>
            <p><span style={{ color: 'var(--color-text-secondary)' }}>Slug:</span> <span style={{ color: 'var(--color-text-primary)' }}>{project.slug}</span></p>
            <p><span style={{ color: 'var(--color-text-secondary)' }}>Volumes:</span> <span style={{ color: 'var(--color-text-primary)' }}>{project.volumes.length}</span></p>
            <p><span style={{ color: 'var(--color-text-secondary)' }}>Language:</span> <span style={{ color: 'var(--color-text-primary)' }}>{project.settings.language}</span></p>
          </div>

          <div className="mt-4 pt-3" style={{ borderTop: '1px solid var(--color-border)' }}>
            <h3 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>DOCX Conversion</h3>
            <button
              className="px-3 py-1.5 text-sm rounded transition-all duration-fast hover:scale-105 disabled:opacity-50"
              style={{
                backgroundColor: convertMutation.isSuccess ? '#10b981' : 'var(--color-accent-primary)',
                color: 'var(--color-bg-primary)'
              }}
              onClick={() => convertMutation.mutate()}
              disabled={convertMutation.isPending}
            >
              {convertMutation.isPending ? 'Converting...' : 'Convert All DOCX'}
            </button>
            {convertMutation.data && (
              <p className="text-sm mt-2" style={{ color: '#10b981' }}>
                Converted {convertMutation.data.converted} files
              </p>
            )}
          </div>
        </section>
      )}

      {/* Create new project */}
      <section className="rounded-lg p-4 animate-fade-in" style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <h2 className="font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>Create New Project</h2>
        <div className="space-y-3">
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--color-text-secondary)' }}>Name</label>
            <input
              type="text"
              className="w-full rounded px-3 py-1.5 text-sm transition-all duration-fast"
              style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-primary)'
              }}
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="My Novel"
            />
          </div>
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--color-text-secondary)' }}>Slug</label>
            <input
              type="text"
              className="w-full rounded px-3 py-1.5 text-sm transition-all duration-fast"
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
            <label className="block text-sm mb-1" style={{ color: 'var(--color-text-secondary)' }}>Description</label>
            <textarea
              className="w-full rounded px-3 py-1.5 text-sm transition-all duration-fast"
              style={{
                backgroundColor: 'var(--color-bg-tertiary)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-primary)'
              }}
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              rows={2}
            />
          </div>
          <button
            className="px-4 py-2 text-sm rounded transition-all duration-fast hover:scale-105 disabled:opacity-50"
            style={{
              backgroundColor: 'var(--color-accent-primary)',
              color: 'var(--color-bg-primary)'
            }}
            onClick={() => createMutation.mutate()}
            disabled={createMutation.isPending || !newName || !newSlug}
          >
            {createMutation.isPending ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </section>
    </div>
  )
}
