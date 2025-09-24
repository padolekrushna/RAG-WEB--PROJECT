# backend/app/core/rag_pipeline.py

from typing import Dict, List, Any
from datetime import datetime
from .vector_store import VectorStore

class RAGPipeline:
    """Simple RAG pipeline using VectorStore"""

    def __init__(self, vector_store: VectorStore, api_key: str):
        self.vector_store = vector_store
        self.api_key = api_key

    def get_response_with_sources(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Generate answer using best chunk from each unique source"""
        results = self.vector_store.search(query, k=k)
        
        if not results:
            return {
                "response": "I couldn't find any relevant information in the uploaded documents.",
                "sources": [],
                "confidence": 0.0,
                "num_sources": 0
            }

        # Group by source_name and keep the highest-scoring chunk per source
        source_map = {}
        for result in results:
            source_name = result["source_name"]
            if source_name not in source_map or result["similarity_score"] > source_map[source_name]["similarity_score"]:
                source_map[source_name] = result

        # Get unique sources (deduplicated)
        unique_sources = list(source_map.values())
        
        # Use top unique source for answer
        top_source = unique_sources[0]
        answer = f"Based on '{top_source['source_name']}':\n\n{top_source['preview']}"
        
        # Optional: Combine multiple unique sources
        # combined_text = "\n\n".join([f"From '{src['source_name']}': {src['preview']}" for src in unique_sources])
        # answer = f"Here's what I found across {len(unique_sources)} documents:\n\n{combined_text}"

        return {
            "response": answer,
            "sources": unique_sources[:3],  # Show up to 3 unique sources
            "confidence": min(0.95, max(0.5, top_source["similarity_score"] + 0.3)),
            "num_sources": len(unique_sources)
        }
    def get_similar_questions(self, query: str, num_questions: int = 3) -> List[str]:
        """Return similar questions (mock)"""
        return [
            f"What is related to {query}?",
            f"How does {query} work?",
            f"Can you explain {query} in detail?"
        ]

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Return stats about the pipeline"""
        return {
            "vector_store_stats": {
                "total_documents": len(self.vector_store.documents) if self.vector_store.documents else 0,
                "embedding_dimension": self.vector_store.embedding_dim,
                "index_size": len(self.vector_store.embeddings) if hasattr(self.vector_store, 'embeddings') else 0,
                "memory_usage": "10 MB (estimated)"
            },
            "last_query_time": datetime.now().isoformat()
        }
    