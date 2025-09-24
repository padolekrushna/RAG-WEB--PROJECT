from typing import Optional
from ..core.rag_pipeline import RAGPipeline

async def get_rag_pipeline() -> Optional[RAGPipeline]:
    """Dependency to get the current RAG pipeline instance"""
    # In a production setup, this would retrieve from a database or cache
    # For now, we'll use the global variable from routes
    from ..api.routes import rag_pipeline
    return rag_pipeline
