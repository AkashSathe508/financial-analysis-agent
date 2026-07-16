import { AnimatePresence, motion, useReducedMotion } from "framer-motion"
import { Check, ChevronDown, CircleDot, Database, FileSearch, Gauge, Newspaper, Search, ShieldCheck, Sparkles, Target } from "lucide-react"
import { useState } from "react"
import type { AgentId, AgentView } from "../../types/stream"
import { cn } from "../../lib/utils"

const icons: Record<AgentId, typeof ShieldCheck> = {
  guard: ShieldCheck, supervisor: Target, entity_extractor: Search, ticker_resolver: CircleDot,
  market: Gauge, news: Newspaper, rag: Database, risk: ShieldCheck, investment: Sparkles, report: FileSearch,
}

function Node({ agent }: { agent: AgentView }) {
  const [open, setOpen] = useState(false)
  const reduced = useReducedMotion()
  const Icon = icons[agent.id]
  return (
    <div className="relative min-w-[116px] md:min-w-0">
      <button onClick={() => agent.output !== undefined && setOpen(!open)} disabled={agent.output === undefined}
        className={cn("group flex w-full items-center gap-2 rounded-lg p-1.5 text-left transition-colors", agent.output !== undefined && "hover:bg-raised")}>
        <motion.span
          animate={agent.status === "running" && !reduced ? { scale: [1, 1.08, 1], boxShadow: ["0 0 0 0 rgba(232,163,61,.1)", "0 0 0 6px rgba(232,163,61,.08)", "0 0 0 0 rgba(232,163,61,.1)"] } : {}}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className={cn("grid size-7 shrink-0 place-items-center rounded-full border text-muted",
            agent.status === "running" && "border-accent bg-accent/10 text-accent",
            agent.status === "done" && "border-accent/50 bg-accent text-[#17120a]",
            agent.status === "error" && "border-loss bg-loss/10 text-loss")}>
          <AnimatePresence mode="wait" initial={false}>
            {agent.status === "done" ? <motion.span key="check" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><Check size={13} strokeWidth={3} /></motion.span> :
              <motion.span key="icon" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><Icon size={13} /></motion.span>}
          </AnimatePresence>
        </motion.span>
        <span className="min-w-0">
          <span className={cn("block truncate text-xs font-medium", agent.status === "pending" ? "text-muted" : "text-ink")}>{agent.label}</span>
          <span className="mono block text-[9px] uppercase tracking-wider text-muted">{agent.status}</span>
        </span>
        {agent.output !== undefined && <ChevronDown size={12} className={cn("ml-auto text-muted transition-transform", open && "rotate-180")} />}
      </button>
      {open && <pre className="mt-1 max-h-40 overflow-auto rounded-md bg-base p-2 text-[9px] leading-4 text-muted">{JSON.stringify(agent.output, null, 2)}</pre>}
      {agent.detail && <p className="mt-1 px-2 text-[10px] text-loss">{agent.detail}</p>}
    </div>
  )
}

export function PipelineRail({ agents }: { agents: AgentView[] }) {
  const before = agents.slice(0, 4)
  const parallel = agents.slice(4, 7)
  const after = agents.slice(7)
  const Connector = () => <div className="mx-4 h-px min-w-4 flex-1 bg-line md:mx-auto md:h-3 md:w-px md:min-w-0 md:flex-none" />
  return (
    <aside aria-label="Analysis pipeline" className="border-b border-line bg-surface p-3 md:h-full md:overflow-y-auto md:border-b-0 md:border-r md:p-4">
      <div className="mb-3 hidden items-center justify-between md:flex">
        <h2 className="mono text-[10px] font-semibold uppercase tracking-[.18em] text-muted">Live pipeline</h2>
        <span className="size-1.5 rounded-full bg-accent" />
      </div>
      <div className="flex items-center overflow-x-auto pb-1 md:block md:overflow-visible">
        {before.map((agent, i) => <div key={agent.id} className="contents"><Node agent={agent} />{i < before.length - 1 && <Connector />}</div>)}
        <Connector />
        <div className="relative flex gap-1 rounded-xl border border-line bg-base/40 p-1 md:my-1 md:block md:space-y-1">
          <span className="mono absolute -top-2 right-2 bg-surface px-1 text-[8px] uppercase tracking-wider text-muted">parallel</span>
          {parallel.map((agent) => <Node key={agent.id} agent={agent} />)}
        </div>
        <Connector />
        {after.map((agent, i) => <div key={agent.id} className="contents"><Node agent={agent} />{i < after.length - 1 && <Connector />}</div>)}
      </div>
    </aside>
  )
}
