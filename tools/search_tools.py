from langchain_tavily import TavilySearch

news_tool = TavilySearch(
    max_results=2,
    topic="news"
)
