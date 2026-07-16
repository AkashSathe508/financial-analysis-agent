import { Area, AreaChart, ResponsiveContainer } from "recharts"
import { ArrowUpRight, Database, Newspaper, Shield, Sparkles } from "lucide-react"
import type { AgentView } from "../../types/stream"

const chart = [{ v: 190 }, { v: 194 }, { v: 192 }, { v: 199 }, { v: 201 }, { v: 198 }, { v: 207 }, { v: 211 }]

function outputOf(agents: AgentView[], id: AgentView["id"]) {
  return agents.find((agent) => agent.id === id)?.output as Record<string, unknown> | undefined
}


export function DataRail({ agents, started }: { agents: AgentView[]; started: boolean }) {
  const marketOutput = outputOf(agents, "market")
  const marketAnalysis = typeof marketOutput?.analysis === "string" ? marketOutput.analysis : ""
  const ticker = String(marketOutput?.ticker ?? marketOutput?.symbol ?? "")
  const marketDone = agents.find((a) => a.id === "market")?.status === "done"
  const ragDone = agents.find((a) => a.id === "rag")?.status === "done"
  const newsDone = agents.find((a) => a.id === "news")?.status === "done"
  const riskDone = agents.find((a) => a.id === "risk")?.status === "done"
  const investmentDone = agents.find((a) => a.id === "investment")?.status === "done"

  // Try to extract company name from market analysis text
  const companyNameMatch = marketAnalysis.match(/^([A-Z][^\n.]+?)(?:\s+is|\s+\(|,|\n)/m)
  const companyDisplay = companyNameMatch ? companyNameMatch[1].trim() : ticker || "Company"

  return (
    <aside className="hidden h-full overflow-y-auto border-l border-line bg-surface p-4 lg:block">
      <p className="mono mb-4 text-[10px] font-semibold uppercase tracking-[.18em] text-muted">Signal desk</p>
      <div className="rounded-xl border border-line bg-base/30 p-4">
        {!marketDone && started ? (
          <div className="space-y-3">
            <div className="skeleton h-4 w-16 rounded" />
            <div className="skeleton h-7 w-28 rounded" />
            <div className="skeleton h-20 rounded" />
          </div>
        ) : marketDone ? (
          <>
            <div className="flex items-start justify-between">
              <div>
                <p className="mono text-xs font-semibold">{ticker || "—"}</p>
                <p className="mt-1 text-[11px] text-muted">{companyDisplay}</p>
              </div>
              <span className="mono flex items-center text-xs text-gain">
                <ArrowUpRight size={13} />
                Live
              </span>
            </div>
            <div className="mt-3 h-20">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chart}>
                  <defs>
                    <linearGradient id="gain" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0" stopColor="#34B37A" stopOpacity=".3" />
                      <stop offset="1" stopColor="#34B37A" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  <Area dataKey="v" stroke="#34B37A" fill="url(#gain)" strokeWidth={1.5} isAnimationActive={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <p className="text-[11px] text-muted">Waiting for market data…</p>
        )}
      </div>
      <div className="mt-3 space-y-2">
        <RailCard
          icon={Newspaper}
          title="News pulse"
          value={newsDone ? "Headlines ready" : started ? "Fetching headlines…" : "Waiting for headlines"}
        />
        <RailCard
          icon={Shield}
          title="Risk profile"
          value={riskDone ? "Assessment ready" : started ? "Analysing signals…" : "Pending market signals"}
        />
        <RailCard
          icon={Sparkles}
          title="Investment view"
          value={investmentDone ? "Verdict ready" : started ? "Synthesising…" : "Synthesis pending"}
        />
        <RailCard
          icon={Database}
          title="Filed reports"
          value={ragDone ? "Annual report searched" : started ? "Searching filings…" : "Annual report available"}
        />
      </div>
    </aside>
  )
}

function RailCard({ icon: Icon, title, value }: { icon: typeof Shield; title: string; value: string }) {
  return (
    <div className="rounded-xl border border-line p-3">
      <div className="flex items-center gap-2 text-xs font-medium">
        <Icon size={14} className="text-accent" />
        {title}
      </div>
      <p className="mt-2 text-[11px] leading-4 text-muted">{value}</p>
    </div>
  )
}
