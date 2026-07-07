import yfinance as yf
from state.financial_state import FinancialState


def ticker_resolver_agent(state: FinancialState):

    company = state["company"]

    search = yf.Search(company)

    quotes = search.quotes

    if not quotes:
        raise ValueError(f"No ticker found for {company}")

    ticker = quotes[0]["symbol"]

    return {
        "ticker": ticker
    }
