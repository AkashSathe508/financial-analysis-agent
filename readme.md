# Financial Analysis Multi-Agent System

A production-grade financial analysis system built with **LangGraph**, **LangChain**, **Google Gemini**, **Groq**, **HuggingFace Embeddings**, **FAISS**, **BM25**, and **Tavily Search**.

## Architecture

```
financial_analysis/
├── app.py                    # Entry point
├── config.py                 # Environment loader
├── requirements.txt
│
├── graphs/
│   ├── main_graph.py         # Main LangGraph assembly
│   └── rag_graph.py          # RAG subgraph assembly
│
├── state/
│   ├── financial_state.py    # FinancialState TypedDict
│   └── rag_state.py          # RAGState TypedDict
│
├── supervisor/
│   └── supervisor.py         # Supervisor agent node
│
├── guardrails/
│   ├── blacklist.py          # Rule-based injection detection
│   ├── models.py             # GuardDecision, CompanyExtraction models
│   ├── prompt_guard.py       # LLM guard node
│   └── router.py             # Guard routing function
│
├── agents/
│   ├── entity_extractor/     # Company name extraction
│   ├── ticker_resolver/      # Yahoo Finance ticker lookup
│   ├── market/               # Market data ReAct agent
│   ├── news/                 # News ReAct agent (Tavily)
│   ├── rag/                  # RAG ReAct agent (preserved)
│   ├── risk/                 # Risk analysis agent
│   ├── investment/           # Investment recommendation agent
│   └── report/               # Final report generator + barrier
│
├── rag/
│   ├── loaders/              # PDF loader
│   ├── splitter/             # RecursiveCharacterTextSplitter
│   ├── embeddings/           # HuggingFace BGE embeddings
│   ├── vectorstores/         # FAISS vector store
│   ├── retrievers/           # Semantic (MultiQuery) + Keyword (BM25)
│   ├── fusion/               # Reciprocal Rank Fusion
│   ├── compression/          # LLMChainExtractor contextual compression
│   ├── self_rag/             # SelfRAG models, evaluator, query rewriter
│   ├── generation/           # Answer generator re-export
│   └── nodes/                # All individual LangGraph RAG nodes
│
├── llms/
│   ├── groq.py               # fast_llm (llama-3.1-8b-instant)
│   └── gemini.py             # reasoning_llm (gemini-2.5-flash)
│
├── tools/
│   ├── market_tools.py       # Yahoo Finance tools
│   ├── search_tools.py       # Tavily news tool
│   └── rag_tools.py          # Financial report retrieval tool
│
└── tests/
```

## Agents

| Agent | Role |
|---|---|
| Supervisor | Validates query relevance |
| Entity Extractor | Extracts company name from query |
| Ticker Resolver | Resolves ticker via Yahoo Finance |
| Market Agent | Fetches live market data (ReAct) |
| News Agent | Fetches latest news via Tavily (ReAct) |
| RAG Agent | Advanced RAG subgraph (Multi-Query + BM25 + RRF + Compression + Self-RAG) |
| Risk Agent | Synthesises risk report |
| Investment Agent | Provides investment recommendation |
| Report Generator | Produces final professional report |

## Running

```bash
python app.py
```

## Data

Place financial report PDFs in:

```
data/reports/
```

The system currently loads `Apple_2025_Annual_Report.pdf`.
