import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Projects
export const listProjects = () => api.get('/projects').then(r => r.data)
export const getProject = (slug: string) => api.get(`/projects/${slug}`).then(r => r.data)
export const createProject = (data: any) => api.post('/projects', data).then(r => r.data)
export const deleteProject = (slug: string) => api.delete(`/projects/${slug}`)

// Chapters
export const listChapters = (slug: string, volume?: number) =>
  api.get(`/projects/${slug}/chapters`, { params: { volume } }).then(r => r.data)
export const readChapter = (slug: string, type: string, number: number, volume: number) =>
  api.get(`/projects/${slug}/chapters/${type}/${number}`, { params: { volume } }).then(r => r.data)

// Drafts
export const listDrafts = (slug: string, volume?: number) =>
  api.get(`/projects/${slug}/chapters/drafts`, { params: { volume } }).then(r => r.data)
export const readDraft = (slug: string, type: string, number: number, volume: number) =>
  api.get(`/projects/${slug}/chapters/drafts/${type}/${number}`, { params: { volume } }).then(r => r.data)
export const saveDraft = (slug: string, type: string, number: number, volume: number, content: string) =>
  api.post(`/projects/${slug}/chapters/${type}/${number}/draft`, { content }, { params: { volume } }).then(r => r.data)
export const submitDraft = (slug: string, type: string, number: number, volume: number) =>
  api.post(`/projects/${slug}/chapters/drafts/${type}/${number}/submit`, null, { params: { volume } }).then(r => r.data)

// Chapter outlines
export const listChapterOutlines = (slug: string, volume?: number) =>
  api.get(`/projects/${slug}/chapters/outlines`, { params: { volume } }).then(r => r.data)
export const readChapterOutlineFile = (
  slug: string,
  type: string,
  number: number,
  volume: number,
  fileKey: 'outline' | 'concept'
) => api.get(`/projects/${slug}/chapters/outlines/${type}/${number}/${fileKey}`, { params: { volume } }).then(r => r.data)
export const saveChapterOutlineFile = (
  slug: string,
  type: string,
  number: number,
  volume: number,
  fileKey: 'outline' | 'concept',
  content: string
) => api.put(`/projects/${slug}/chapters/outlines/${type}/${number}/${fileKey}`, { content }, { params: { volume } }).then(r => r.data)

// Lore
export const getLoreSnapshot = (slug: string) =>
  api.get(`/projects/${slug}/lore/snapshot`).then(r => r.data)
export const getLoreDetails = (slug: string, ids: string[]) =>
  api.post(`/projects/${slug}/lore/details`, ids).then(r => r.data)
export const searchLore = (slug: string, keyword: string, category?: string) =>
  api.post(`/projects/${slug}/lore/search`, null, { params: { keyword, category } }).then(r => r.data)
export const proposePatch = (slug: string, data: any) =>
  api.post(`/projects/${slug}/lore/patch/propose`, data).then(r => r.data)
export const commitPatch = (slug: string, patchId: string) =>
  api.post(`/projects/${slug}/lore/patch/${patchId}/commit`).then(r => r.data)
export const updateLoreEntry = (
  slug: string,
  category: string,
  name: string,
  data: { content: string; metadata?: Record<string, any> }
) => api.put(`/projects/${slug}/lore/${category}/${name}`, data).then(r => r.data)
export const getIndexFiles = (slug: string) =>
  api.get(`/projects/${slug}/lore/index`).then(r => r.data)

// Memory
export const queryMemory = (slug: string, query: string, topK: number = 5) =>
  api.post(`/projects/${slug}/memory/query`, { query, top_k: topK }).then(r => r.data)
export const getMemoryCount = (slug: string) =>
  api.get(`/projects/${slug}/memory/count`).then(r => r.data)

// Converter
export const convertDocx = (slug: string, volumeDir?: string) =>
  api.post(`/projects/${slug}/convert`, { volume_dir: volumeDir }).then(r => r.data)

// Knowledge
export const listProjectKnowledge = (slug: string) =>
  api.get(`/projects/${slug}/knowledge`).then(r => r.data)
export const readKnowledge = (path: string, slug?: string) =>
  api.get(`/knowledge/${encodeURIComponent(path)}`, { params: { slug } }).then(r => r.data)
export const updateKnowledge = (path: string, content: string, slug?: string) =>
  api.put(`/knowledge/${encodeURIComponent(path)}`, { content }, { params: { slug } }).then(r => r.data)

// OpsasPlan
export const listOpsasCategories = () =>
  api.get('/opsas/categories').then(r => r.data)
export const listOpsasPlans = (category?: string) =>
  api.get('/opsas/plans', { params: { category } }).then(r => r.data)
export const readOpsasPlan = (category: string, name: string) =>
  api.get(`/opsas/plans/${encodeURIComponent(category)}/${encodeURIComponent(name)}`).then(r => r.data)
export const writeOpsasPlan = (category: string, name: string, content: string) =>
  api.put(`/opsas/plans/${encodeURIComponent(category)}/${encodeURIComponent(name)}`, { content }).then(r => r.data)
export const deleteOpsasPlan = (category: string, name: string) =>
  api.delete(`/opsas/plans/${encodeURIComponent(category)}/${encodeURIComponent(name)}`).then(r => r.data)
export const createOpsasPlan = (data: { category: string; title: string; slug?: string; tags?: string[] }) =>
  api.post('/opsas/plans', data).then(r => r.data)

export default api
