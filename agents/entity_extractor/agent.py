import logging
import re

from state.financial_state import FinancialState
from guardrails.models import CompanyExtraction
from llms.gemini import reasoning_llm

logger = logging.getLogger(__name__)

# =========================================================
# STRUCTURE MODEL
# =========================================================
extractor_llm = reasoning_llm.with_structured_output(
    CompanyExtraction
)


def _fallback_company(query: str) -> str:
    query = query.strip()
    match = re.search(
        r"(?:analyze|about|for|in|on|invest in|stock of)\s+([A-Za-z][A-Za-z0-9 .&-]*)",
        query,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).strip(" .?")

    cleaned = re.sub(r"[^A-Za-z0-9 .&-]", " ", query)
    cleaned = re.sub(
        r"\b(analyze|analysis|stock|shares|company|should|i|invest|in|the|of|for|about|please|tell|me)\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", cleaned).strip(" .") or query


def entity_extractor_agent(state: FinancialState):

    query = state["query"]
    prompt = f"""
        You are a financial entity extraction agent.

        Extract ONLY the company name mentioned.

        Examples

        Input:
        Should I invest in Apple?

        Output:
        Apple

        Input:
        Analyze Microsoft stock.

        Output:
        Microsoft

        Input:
        Tell me about Tesla.

        Output:
        Tesla

        User Query:

        {query}
    """

    try:
        result = extractor_llm.invoke(prompt)
        company = result.company
    except Exception as exc:
        logger.warning("Entity extraction failed; using heuristic fallback: %s", exc)
        company = state.get("company") or _fallback_company(query)

    logger.info("Extracted company: %s", company)
    return {
        "company": company
    }
