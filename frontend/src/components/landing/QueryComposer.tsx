import { ArrowUp, FileText, Loader2, Square, Upload } from "lucide-react"
import type { ChangeEvent, FormEvent, KeyboardEvent } from "react"

const examples = ["Analyze Apple.", "Assess Apple's key risks.", "Is Apple a good long-term investment?"]

interface Props {
  value: string
  isStreaming: boolean
  compact?: boolean
  documentName?: string
  uploadError?: string
  isUploading?: boolean
  onChange: (value: string) => void
  onUpload: (file: File) => void
  onRun: () => void
  onStop: () => void
}

export function QueryComposer({
  value,
  isStreaming,
  compact,
  documentName,
  uploadError,
  isUploading,
  onChange,
  onUpload,
  onRun,
  onStop,
}: Props) {
  const submit = (event: FormEvent) => {
    event.preventDefault()
    if (value.trim() && !isStreaming) onRun()
  }
  const keyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      if (value.trim() && !isStreaming) onRun()
    }
  }
  const upload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ""
    if (file) onUpload(file)
  }

  return (
    <div className={compact ? "w-full" : "mx-auto w-full max-w-2xl"}>
      {!compact && (
        <div className="mb-8 text-center">
          <p className="mono mb-3 text-[11px] uppercase tracking-[.2em] text-accent">Multi-agent financial intelligence</p>
          <h1 className="text-3xl font-semibold tracking-[-.045em] sm:text-4xl">What should we analyze?</h1>
          <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-muted">Ten specialist agents examine market data, filings, news, risk, and investment fit while you watch the work happen.</p>
        </div>
      )}
      <form onSubmit={submit} className="panel rounded-2xl p-2 shadow-2xl shadow-black/10 focus-within:border-accent/60">
        <label htmlFor="analysis-query" className="sr-only">Financial analysis query</label>
        <textarea
          id="analysis-query"
          rows={compact ? 1 : 3}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={keyDown}
          placeholder="Ask about a public company..."
          className="block w-full resize-none bg-transparent px-3 py-2.5 text-[15px] placeholder:text-muted/70"
        />
        <div className="flex flex-col gap-2 px-1 pb-1 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2 px-2">
            <label className="flex h-9 cursor-pointer items-center gap-2 rounded-lg border border-line px-3 text-xs font-medium text-muted hover:bg-raised hover:text-ink">
              {isUploading ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
              {isUploading ? "Processing PDF" : documentName ? "Replace PDF" : "Upload PDF"}
              <input type="file" accept="application/pdf,.pdf" className="sr-only" disabled={isUploading || isStreaming} onChange={upload} />
            </label>
            {documentName && (
              <span className="flex min-w-0 items-center gap-1.5 text-xs text-muted">
                <FileText size={13} className="shrink-0 text-accent" />
                <span className="truncate">{documentName}</span>
              </span>
            )}
            {uploadError && <span className="text-xs text-loss">{uploadError}</span>}
          </div>
          {isStreaming ? (
            <button type="button" onClick={onStop} className="ml-auto flex h-9 items-center gap-2 rounded-lg bg-ink px-3 text-sm font-medium text-base">
              <Square size={12} fill="currentColor" /> Stop
            </button>
          ) : (
            <button type="submit" disabled={!value.trim() || isUploading} className="ml-auto flex h-9 items-center gap-2 rounded-lg bg-accent px-3 text-sm font-semibold text-[#17120a] transition-transform hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-40">
              Run analysis <ArrowUp size={15} />
            </button>
          )}
        </div>
      </form>
      {!compact && (
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {examples.map((example) => (
            <button key={example} onClick={() => onChange(example)} className="rounded-full border border-line bg-surface px-3 py-1.5 text-xs text-muted hover:border-accent/40 hover:text-ink">{example}</button>
          ))}
        </div>
      )}
    </div>
  )
}
