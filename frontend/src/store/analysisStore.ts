import { create } from "zustand"

type Theme = "dark" | "light"
interface HistoryItem { query: string; createdAt: number }
interface AnalysisStore {
  query: string
  theme: Theme
  history: HistoryItem[]
  setQuery: (query: string) => void
  toggleTheme: () => void
  addHistory: (query: string) => void
  reset: () => void
}

const savedTheme = (localStorage.getItem("ledger-theme") as Theme | null) ?? "dark"
const savedHistory = (() => {
  try { return JSON.parse(localStorage.getItem("ledger-history") ?? "[]") as HistoryItem[] }
  catch { return [] }
})()

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  query: "",
  theme: savedTheme,
  history: savedHistory,
  setQuery: (query) => set({ query }),
  toggleTheme: () => set((state) => {
    const theme = state.theme === "dark" ? "light" : "dark"
    localStorage.setItem("ledger-theme", theme)
    return { theme }
  }),
  addHistory: (query) => set((state) => {
    const history = [{ query, createdAt: Date.now() }, ...state.history].slice(0, 12)
    localStorage.setItem("ledger-history", JSON.stringify(history))
    return { history }
  }),
  reset: () => set({ query: "" }),
}))
