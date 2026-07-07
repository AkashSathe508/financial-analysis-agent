from langchain_groq import ChatGroq

# =========================================================
# NORMAL LLM
# =========================================================
fast_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)
