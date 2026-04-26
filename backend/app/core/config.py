from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # LLM
    OPENAI_API_KEY: str
    GROQ_API_KEY: Optional[str] = Field(default=None)
    GROQ_MODEL_NAME: str = Field(default="llama3-70b-8192")
    
    # DATABASE
    DATABASE_URL: str = Field(default="sqlite:///./lawassist.db", env="DATABASE_URL")
    
    # TRELLO
    TRELLO_API_KEY: str
    TRELLO_TOKEN: str
    TRELLO_BOARD_ID: str
    TRELLO_LIST_ID_CLIENTS: str
    
    # GOOGLE
    GOOGLE_SERVICE_ACCOUNT_FILE: str = "service-account.json"
    GOOGLE_DRIVE_PARENT_FOLDER_ID: str
    GOOGLE_DOCS_CONTRACT_TEMPLATE_ID: str
    
    # EVOLUTION API
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str
    EVOLUTION_INSTANCE_NAME: str
    
    # SUPABASE AUTH
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_KEY: Optional[str] = Field(default=None)
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None)
    
    # APP
    DEBUG: bool = True
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
