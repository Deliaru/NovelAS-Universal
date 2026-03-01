import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useProjectStore } from '../store/projectStore'
import { getProject, createProject, listProjects, convertDocx } from '../api/client'
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
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      {/* Current project info */}
      {project && (
        <section className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <h2 className="font-semibold mb-3">Current Project</h2>
          <div className="text-sm space-y-1">
            <p><span className="text-gray-500">Name:</span> {project.name}</p>
            <p><span className="text-gray-500">Slug:</span> {project.slug}</p>
            <p><span className="text-gray-500">Volumes:</span> {project.volumes.length}</p>
            <p><span className="text-gray-500">Language:</span> {project.settings.language}</p>
          </div>

          <div className="mt-4 pt-3 border-t border-gray-100">
            <h3 className="text-sm font-medium mb-2">DOCX Conversion</h3>
            <button
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              onClick={() => convertMutation.mutate()}
              disabled={convertMutation.isPending}
            >
              {convertMutation.isPending ? 'Converting...' : 'Convert All DOCX'}
            </button>
            {convertMutation.data && (
              <p className="text-sm text-green-600 mt-2">
                Converted {convertMutation.data.converted} files
              </p>
            )}
          </div>
        </section>
      )}

      {/* Create new project */}
      <section className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="font-semibold mb-3">Create New Project</h2>
        <div className="space-y-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Name</label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="My Novel"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Slug</label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              value={newSlug}
              onChange={(e) => setNewSlug(e.target.value)}
              placeholder="my-novel"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Description</label>
            <textarea
              className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              rows={2}
            />
          </div>
          <button
            className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
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
