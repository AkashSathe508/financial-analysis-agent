import yfinance as yf

# =========================================================
# HELPER FUNCTION
# =========================================================
def fetch_company_info(symbol: str):

    stock = yf.Ticker(symbol)

    return stock.info
