import { BarChart3, Moon, Plus, Sun } from "lucide-react"

interface Props {
  theme: "dark" | "light"
  currentQuery?: string
  onToggleTheme: () => void
  onNew: () => void
}

export function TopBar({ theme, currentQuery, onToggleTheme, onNew }: Props) {
  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b border-line px-4 sm:px-6">
      <div className="flex items-center gap-2.5">
        <span className="grid size-8 place-items-center rounded-lg border border-accent/35 bg-accent/10 text-accent">
          <BarChart3 size={17} aria-hidden />
        </span>
        <span className="font-semibold tracking-[-0.03em]">Ledger</span>
      </div>
      {currentQuery && <p className="ml-3 hidden truncate border-l border-line pl-5 text-sm text-muted md:block">{currentQuery}</p>}
      <div className="ml-auto flex items-center gap-2">
        <button onClick={onToggleTheme} className="grid size-9 place-items-center rounded-lg border border-line text-muted hover:bg-raised hover:text-ink" aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}>
          {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>
        <button onClick={onNew} className="flex h-9 items-center gap-2 rounded-lg border border-line px-3 text-sm font-medium hover:bg-raised">
          <Plus size={15} /> <span className="hidden sm:inline">New analysis</span>
        </button>
      </div>
    </header>
  )
}
