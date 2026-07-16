import { ArrowDown, FileText } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeSanitize from "rehype-sanitize"
import { useAutoScroll } from "../../hooks/useAutoScroll"

interface Props { report: string; isStreaming: boolean; started: boolean }

export function ReportStream({ report, isStreaming, started }: Props) {
  const scroll = useAutoScroll(report)
  return (
    <section className="relative min-h-0 flex-1">
      <div ref={scroll.ref} onScroll={scroll.onScroll} className="h-full overflow-y-auto px-5 py-7 sm:px-8 lg:px-10">
        <div className="mx-auto max-w-3xl">
          {!report && started && (
            <div className="space-y-5" aria-label="Preparing report">
              <div className="mb-8 flex items-center gap-3 text-sm text-muted"><FileText size={16} className="text-accent" />Building the analysis as agents finish their work…</div>
              <div className="skeleton h-8 w-2/3 rounded" /><div className="skeleton h-3 w-full rounded" /><div className="skeleton h-3 w-11/12 rounded" />
              <div className="skeleton mt-9 h-5 w-1/3 rounded" /><div className="skeleton h-3 w-full rounded" /><div className="skeleton h-3 w-4/5 rounded" />
            </div>
          )}
          {report && <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>{report}</ReactMarkdown>{isStreaming && <span className="stream-caret" aria-hidden />}</div>}
        </div>
      </div>
      {!scroll.pinned && isStreaming && <button onClick={scroll.jump} className="absolute bottom-4 left-1/2 flex -translate-x-1/2 items-center gap-1.5 rounded-full border border-line bg-raised px-3 py-1.5 text-xs shadow-xl"><ArrowDown size={13} /> Jump to latest</button>}
    </section>
  )
}
