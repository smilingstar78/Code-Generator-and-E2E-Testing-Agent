from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    LLM_PROVIDER: Literal["groq", "openai", "ollama"] = "groq"
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    MAX_RETRY_ITERATIONS: int = 3
    CONTAINER_TIMEOUT_SECONDS: int = 15

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()