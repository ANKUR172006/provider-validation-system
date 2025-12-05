import { create } from 'zustand'

interface AppState {
  currentJobId: string | null
  setCurrentJobId: (jobId: string | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  currentJobId: null,
  setCurrentJobId: (jobId) => set({ currentJobId: jobId }),
}))


