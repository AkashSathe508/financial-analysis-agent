import { useCallback, useRef, useState } from "react"
import { extractSseFrames } from "../lib/sse"
import type { StreamEvent } from "../types/stream"

export function useAgentStream() {
  const [events, setEvents] = useState<StreamEvent[]>([])
  const [reportText, setReportText] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const tokenQueue = useRef("")
  const frameRef = useRef<number | null>(null)

  const flushTokens = useCallback(() => {
    if (tokenQueue.current) {
      const next = tokenQueue.current
      tokenQueue.current = ""
      setReportText((prev) => prev + next)
    }
    frameRef.current = null
  }, [])

  const run = useCallback(async (query: string, sessionId?: string) => {
    setEvents([{ type: "run_started", query }])
    setReportText("")
    setIsStreaming(true)
    const controller = new AbortController()
    abortRef.current = controller
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(sessionId ? { "X-Session-ID": sessionId } : {}),
        },
        body: JSON.stringify({ query, session_id: sessionId }),
        signal: controller.signal,
      })
      if (!response.ok || !response.body) throw new Error(`Analysis service returned ${response.status}.`)
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const parsed = extractSseFrames(buffer)
        buffer = parsed.rest
        for (const event of parsed.events) {
          setEvents((prev) => [...prev, event])
          if (event.type === "report_token") {
            tokenQueue.current += event.token
            if (frameRef.current === null) frameRef.current = requestAnimationFrame(flushTokens)
          }
        }
      }
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        setEvents((prev) => [...prev, { type: "error", message: (error as Error).message }])
      }
    } finally {
      flushTokens()
      setIsStreaming(false)
      abortRef.current = null
    }
  }, [flushTokens])

  const stop = useCallback(() => abortRef.current?.abort(), [])
  const clear = useCallback(() => { setEvents([]); setReportText("") }, [])
  return { events, reportText, isStreaming, run, stop, clear }
}
