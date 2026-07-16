import re
import time

from langchain_groq import ChatGroq

# =========================================================
# NORMAL LLM
# =========================================================
fast_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_retries=5,
    max_tokens=700,
    timeout=60,
)


_RATE_LIMIT_DELAY_RE = re.compile(r"try again in ([0-9.]+)s", re.IGNORECASE)


def invoke_with_rate_limit_retry(runnable, input, *, attempts: int = 4):
    for attempt in range(attempts):
        try:
            return runnable.invoke(input)
        except Exception as exc:
            is_rate_limit = getattr(exc, "status_code", None) == 429 or "rate limit" in str(exc).lower()
            if not is_rate_limit or attempt == attempts - 1:
                raise

            match = _RATE_LIMIT_DELAY_RE.search(str(exc))
            delay = float(match.group(1)) if match else min(2**attempt, 8)
            time.sleep(delay + 0.5)
