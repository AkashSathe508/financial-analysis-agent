from langchain_google_genai import ChatGoogleGenerativeAI

# =========================================================
# NORMAL LLM
# =========================================================
reasoning_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)
