export interface Project {
  slug: string
  name: string
  description: string
  volumes: Volume[]
  settings: ProjectSettings
}

export interface ProjectSummary {
  slug: string
  name: string
  description: string
  volume_count: number
  chapter_count: number
  lore_count: number
}

export interface Volume {
  number: number
  title: string
  source_dir: string
}

export interface ProjectSettings {
  language: string
  embedding_model: string
  ai_provider: string | null
  prohibited_words: string[]
  style_reference: string | null
}

export type ChapterType = 'Prologue' | 'Chapter' | 'Interlude' | 'Extra' | 'Finale'

export interface ChapterListItem {
  type: ChapterType
  volume: number
  number: number
  filename: string
  display_name: string
  word_count: number
}

export interface ChapterContent {
  type: ChapterType
  volume: number
  number: number
  filename: string
  display_name: string
  content: string
  word_count: number
}

export interface LoreEntry {
  id: string
  name: string
  category: string
  summary: string
  metadata: Record<string, any>
}

export interface LoreSnapshot {
  entries: LoreEntry[]
  total: number
}

export interface LoreSearchResult {
  id: string
  name: string
  category: string
  excerpt: string
  score: number
}
