from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_path: str
    size: int
    content_type: str
    upload_timestamp: str

class ProcessDocumentsRequest(BaseModel):
    file_ids: List[str]
    api_key: str
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200

class ProcessDocumentsResponse(BaseModel):
    success: bool
    message: str
    total_chunks: int
    processed_files: List[Dict[str, Any]]
    processing_timestamp: str

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    k: Optional[int] = Field(default=5, ge=1, le=20)
    include_sources: Optional[bool] = True

class SourceInfo(BaseModel):
    chunk_id: int
    similarity_score: float
    preview: str
    source_name: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[SourceInfo]
    confidence: float
    num_sources: int
    response_timestamp: str

class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    embedding_dimension: int
    index_size: int
    memory_usage: str
    status: str

class SimilarQuestionsResponse(BaseModel):
    query: str
    similar_questions: List[str]
    count: int

class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str