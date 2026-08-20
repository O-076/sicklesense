import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "https://creativa-hackathon-vb.search.windows.net")
    AZURE_SEARCH_KEY: str = os.getenv("AZURE_SEARCH_KEY", "")
    AZURE_SEARCH_INDEX: str = os.getenv("AZURE_SEARCH_INDEX", "creativa-hackathon-pc")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
