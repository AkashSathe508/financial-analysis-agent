import { useEffect, useMemo, useState } from "react"
import { TopBar } from "./components/layout/TopBar"
import { QueryComposer } from "./components/landing/QueryComposer"
import { PipelineRail } from "./components/pipeline/PipelineRail"
import { ReportStream } from "./components/report/ReportStream"
import { DataRail } from "./components/data-rail/DataRail"
import { ErrorPanel, GuardBlocked } from "./components/states/RunStates"
import { useAgentStream } from "./hooks/useAgentStream"
import { useAnalysisStore } from "./store/analysisStore"
import type { AgentId, AgentView } from "./types/stream"

const stages: { id: AgentId; label: string }[] = [
  { id: "guard", label: "Guard" }, { id: "supervisor", label: "Supervisor" },
  { id: "entity_extractor", label: "Entity extractor" }, { id: "ticker_resolver", label: "Ticker resolver" },
  { id: "market", label: "Market" }, { id: "news", label: "News" }, { id: "rag", label: "Filings RAG" },
  { id: "risk", label: "Risk" }, { id: "investment", label: "Investment" }, { id: "report", label: "Report" },
]

const savedSessionId = localStorage.getItem("ledger-session-id") ?? ""
const savedDocumentName = localStorage.getItem("ledger-document-name") ?? ""

export function App() {
  const store = useAnalysisStore()
  const stream = useAgentStream()
  const [sessionId, setSessionId] = useState(savedSessionId)
  const [documentName, setDocumentName] = useState(savedDocumentName)
  const [uploadError, setUploadError] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const started = stream.events.length > 0
  const blocked = stream.events.find((e) => e.type === "blocked")
  const error = [...stream.events].reverse().find((e) => e.type === "error")
  const complete = stream.events.some((e) => e.type === "run_completed")
  const currentQuery = stream.events.find((e) => e.type === "run_started")

  const agents = useMemo<AgentView[]>(() => stages.map((stage) => {
    const statusEvents = stream.events.filter((e) => e.type === "agent_status" && e.agent === stage.id)
    const latest = statusEvents.at(-1)
    const output = [...stream.events].reverse().find((e) => e.type === "agent_output" && e.agent === stage.id)
    return { ...stage, status: latest?.type === "agent_status" ? latest.status : "pending", detail: latest?.type === "agent_status" ? latest.detail : undefined, output: output?.type === "agent_output" ? output.output : undefined }
  }), [stream.events])

  useEffect(() => {
    document.documentElement.classList.toggle("light", store.theme === "light")
    document.documentElement.classList.toggle("dark", store.theme === "dark")
  }, [store.theme])
  useEffect(() => {
    const stopOnEscape = (event: KeyboardEvent) => { if (event.key === "Escape" && stream.isStreaming) stream.stop() }
    window.addEventListener("keydown", stopOnEscape)
    return () => window.removeEventListener("keydown", stopOnEscape)
  }, [stream.isStreaming, stream.stop])

  const uploadPdf = async (file: File) => {
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setUploadError("Choose a PDF annual report.")
      return
    }

    setIsUploading(true)
    setUploadError("")
    try {
      const form = new FormData()
      form.append("file", file)
      if (sessionId) form.append("session_id", sessionId)

      const response = await fetch("/api/upload", {
        method: "POST",
        body: form,
      })
      const payload = await response.json().catch(() => ({}))
      if (!response.ok || !payload.success) {
        throw new Error(payload.message ?? `Upload failed with status ${response.status}.`)
      }

      setSessionId(payload.session_id)
      setDocumentName(file.name)
      localStorage.setItem("ledger-session-id", payload.session_id)
      localStorage.setItem("ledger-document-name", file.name)
    } catch (error) {
      setUploadError((error as Error).message)
    } finally {
      setIsUploading(false)
    }
  }

  const run = () => {
    const query = store.query.trim()
    if (!query) return
    if (!sessionId) {
      setUploadError("Upload a PDF before running analysis.")
      return
    }
    setUploadError("")
    store.addHistory(query)
    stream.run(query, sessionId)
  }
  const reset = () => { stream.clear(); store.reset() }

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-base text-ink">
      <TopBar theme={store.theme} currentQuery={currentQuery?.type === "run_started" ? currentQuery.query : undefined} onToggleTheme={store.toggleTheme} onNew={reset} />
      {!started ? (
        <main className="relative grid flex-1 place-items-center overflow-y-auto px-4 py-12">
          <div className="subtle-grid pointer-events-none absolute inset-0 opacity-50" />
          <div className="relative w-full"><QueryComposer value={store.query} isStreaming={stream.isStreaming} documentName={documentName} uploadError={uploadError} isUploading={isUploading} onChange={store.setQuery} onUpload={uploadPdf} onRun={run} onStop={stream.stop} /></div>
        </main>
      ) : (
        <main className="grid min-h-0 flex-1 grid-rows-[auto_1fr] md:grid-cols-[190px_minmax(0,1fr)] md:grid-rows-1 lg:grid-cols-[200px_minmax(0,1fr)_240px]">
          <PipelineRail agents={agents} />
          <div className="flex min-h-0 flex-col">
            <div className="min-h-0 flex-1">
              {blocked?.type === "blocked" ? <GuardBlocked message={blocked.response} onReset={reset} /> :
                error?.type === "error" && !stream.reportText ? <ErrorPanel message={error.message} onRetry={run} /> :
                  <ReportStream report={stream.reportText} isStreaming={stream.isStreaming && !complete} started={started} />}
            </div>
            <div className="border-t border-line bg-base/80 p-3 backdrop-blur"><div className="mx-auto max-w-3xl"><QueryComposer compact value={store.query} isStreaming={stream.isStreaming} documentName={documentName} uploadError={uploadError} isUploading={isUploading} onChange={store.setQuery} onUpload={uploadPdf} onRun={run} onStop={stream.stop} /></div></div>
          </div>
          <DataRail agents={agents} started={started} />
        </main>
      )}
      <div aria-live="polite" className="sr-only">{complete ? "Analysis complete." : agents.filter((a) => a.status === "done").at(-1)?.label ? `${agents.filter((a) => a.status === "done").at(-1)?.label} agent complete.` : ""}</div>
    </div>
  )
}
