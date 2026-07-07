import config  # noqa: F401 — loads .env before any LLM clients are initialised
from graphs.main_graph import graph

if __name__ == "__main__":
    query = "Analyze Apple."

    result = graph.invoke(
        {
            "query": query,
            "company": "",
            "ticker": "",
            "agent_outputs": {},
            "final_report": "",
            "blocked": False,
            "response": "",
            "messages": []
        }
    )

    print(result['final_report'])
