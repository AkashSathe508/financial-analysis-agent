import { AlertTriangle, RotateCcw, ShieldAlert } from "lucide-react"

export function GuardBlocked({ message, onReset }: { message: string; onReset: () => void }) {
  return <div className="mx-auto my-10 max-w-lg rounded-2xl border border-accent/30 bg-accent/5 p-6"><ShieldAlert className="text-accent" /><h2 className="mt-4 text-lg font-semibold">This analysis can’t continue</h2><p className="mt-2 text-sm leading-6 text-muted">{message}</p><button onClick={onReset} className="mt-5 rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-[#17120a]">Try a different query</button></div>
}

export function ErrorPanel({ message, onRetry }: { message: string; onRetry: () => void }) {
  const needsPdf = message.toLowerCase().includes("upload a pdf")
  return <div className="mx-auto my-10 max-w-lg rounded-2xl border border-loss/30 bg-loss/5 p-6"><AlertTriangle className="text-loss" /><h2 className="mt-4 text-lg font-semibold">{needsPdf ? "Upload a PDF first" : "The connection dropped"}</h2><p className="mt-2 text-sm leading-6 text-muted">{message}</p><button onClick={onRetry} className="mt-5 flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm font-medium"><RotateCcw size={14} />Retry analysis</button></div>
}
