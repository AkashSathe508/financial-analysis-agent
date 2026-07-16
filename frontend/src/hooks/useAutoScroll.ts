import { useCallback, useEffect, useRef, useState } from "react"

export function useAutoScroll(dependency: unknown) {
  const ref = useRef<HTMLDivElement>(null)
  const [pinned, setPinned] = useState(true)
  const onScroll = useCallback(() => {
    const element = ref.current
    if (!element) return
    setPinned(element.scrollHeight - element.scrollTop - element.clientHeight < 80)
  }, [])
  useEffect(() => {
    if (pinned) ref.current?.scrollTo({ top: ref.current.scrollHeight, behavior: "smooth" })
  }, [dependency, pinned])
  const jump = useCallback(() => {
    setPinned(true)
    ref.current?.scrollTo({ top: ref.current.scrollHeight, behavior: "smooth" })
  }, [])
  return { ref, pinned, onScroll, jump }
}
