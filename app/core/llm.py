from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm():
    """
    Returns an LLM client based on the LLM_PROVIDER setting in .env.
    Uses Groq's active openai/gpt-oss-120b model.
    """
    if settings.LLM_PROVIDER == "groq":
        return ChatGroq(
            temperature=0.1,
            model_name="openai/gpt-oss-120b",
            api_key=settings.GROQ_API_KEY
        )
    elif settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            temperature=0.1,
            model_name="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY
        )
    else:
        raise ValueError(f"Unsupported LLM Provider: {settings.LLM_PROVIDER}")