from __future__ import annotations

import logging

import yfinance as yf

from state.financial_state import FinancialState

logger = logging.getLogger(__name__)

# Well-known tickers for common companies used as a last-resort fallback
# so the graph never crashes due to a failed ticker lookup.
_FALLBACK_TICKERS: dict[str, str] = {
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "meta": "META",
    "tesla": "TSLA",
    "nvidia": "NVDA",
    "netflix": "NFLX",
    "berkshire": "BRK-B",
}


def _lookup_ticker(company: str) -> str:
    """Search yfinance for the best-matching ticker symbol."""
    search = yf.Search(company)
    quotes = search.quotes
    if quotes:
        return quotes[0]["symbol"]
    raise ValueError(f"No ticker found for '{company}'")


def _fallback_ticker(company: str) -> str | None:
    """Return a hardcoded ticker when the API lookup fails."""
    key = company.lower().strip()
    for name, ticker in _FALLBACK_TICKERS.items():
        if name in key:
            return ticker
    return None


def ticker_resolver_agent(state: FinancialState) -> dict:
    company = state["company"]

    if not company:
        logger.warning("Ticker resolver received an empty company name; skipping.")
        return {"ticker": ""}

    try:
        ticker = _lookup_ticker(company)
        logger.info("Resolved ticker for '%s': %s", company, ticker)
        return {"ticker": ticker}
    except Exception as exc:
        logger.warning("yfinance ticker lookup failed for '%s': %s", company, exc)

    # Try hardcoded fallback before giving up
    fallback = _fallback_ticker(company)
    if fallback:
        logger.info("Using fallback ticker for '%s': %s", company, fallback)
        return {"ticker": fallback}

    # Return empty string — downstream agents must handle missing ticker gracefully
    logger.error("Could not resolve ticker for '%s'; proceeding with empty ticker.", company)
    return {"ticker": ""}
