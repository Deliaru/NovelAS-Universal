import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ProjectState {
  currentSlug: string | null
  setCurrentSlug: (slug: string | null) => void
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      currentSlug: null,
      setCurrentSlug: (slug) => set({ currentSlug: slug }),
    }),
    { name: 'novelas-project' }
  )
)
