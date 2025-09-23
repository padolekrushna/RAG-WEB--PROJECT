# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG Document Q&A API"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://your-frontend-domain.com",
        # Add your Azure frontend URL here
    ]
    
    # Database/Storage (for future use)
    DATABASE_URL: str = "sqlite:///./storage/rag_system.db"
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "txt", "docx"]
    UPLOAD_DIR: str = "storage/uploads"
    INDEX_DIR: str = "storage/indexes"
    
    # Azure Configuration
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_CONTAINER_NAME: str = "rag-documents"
    
    # API Keys (these should be set via environment variables)
    GOOGLE_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()

# backend/app/api/dependencies.py
from typing import Optional
from ..core.rag_pipeline import RAGPipeline

async def get_rag_pipeline() -> Optional[RAGPipeline]:
    """Dependency to get the current RAG pipeline instance"""
    # In a production setup, this would retrieve from a database or cache
    # For now, we'll use the global variable from routes
    from ..api.routes import rag_pipeline
    return rag_pipeline
