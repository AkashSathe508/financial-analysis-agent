import type { AgentId, StreamEvent } from "../types/stream"

const aliases: Record<string, AgentId> = {
  prompt_guard: "guard",
  guard: "guard",
  supervisor: "supervisor",
  entity_extractor: "entity_extractor",
  ticker_resolver: "ticker_resolver",
  market_agent: "market",
  market: "market",
  news_agent: "news",
  news: "news",
  rag_agent: "rag",
  rag: "rag",
  risk_agent: "risk",
  risk: "risk",
  investment_agent: "investment",
  investment: "investment",
  report_generator: "report",
  report: "report",
}

export function normalizeEvent(value: unknown): StreamEvent {
  const event = value as Record<string, unknown>
  if (typeof event.agent === "string" && aliases[event.agent]) {
    return { ...event, agent: aliases[event.agent] } as StreamEvent
  }
  return event as StreamEvent
}

export function extractSseFrames(buffer: string) {
  const chunks = buffer.replace(/\r\n/g, "\n").split("\n\n")
  const rest = chunks.pop() ?? ""
  const events: StreamEvent[] = []
  for (const chunk of chunks) {
    const payload = chunk
      .split("\n")
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trimStart())
      .join("\n")
    if (!payload) continue
    try {
      events.push(normalizeEvent(JSON.parse(payload)))
    } catch {
      // Ignore malformed frames while allowing the stream to continue.
    }
  }
  return { events, rest }
}
