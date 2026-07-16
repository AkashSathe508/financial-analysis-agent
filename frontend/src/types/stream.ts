export type AgentId =
  | "guard"
  | "supervisor"
  | "entity_extractor"
  | "ticker_resolver"
  | "market"
  | "news"
  | "rag"
  | "risk"
  | "investment"
  | "report"

export type AgentStatus = "pending" | "running" | "done" | "error"

export type StreamEvent =
  | { type: "run_started"; query: string }
  | { type: "agent_status"; agent: AgentId; status: Exclude<AgentStatus, "pending">; detail?: string }
  | { type: "agent_output"; agent: AgentId; output: unknown }
  | { type: "report_token"; token: string }
  | { type: "blocked"; response: string }
  | { type: "error"; message: string }
  | { type: "run_completed" }

export interface AgentView {
  id: AgentId
  label: string
  status: AgentStatus
  output?: unknown
  detail?: string
}
