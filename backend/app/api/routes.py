# backend/app/api/routes.py
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
import shutil
from datetime import datetime

from ..models.schemas import (
    QueryRequest, QueryResponse, DocumentUploadResponse, 
    ProcessDocumentsRequest, ProcessDocumentsResponse,
    SystemStats, HealthResponse
)
from ..core.document_processor import DocumentProcessor
from ..core.vector_store import VectorStore
from ..core.rag_pipeline import RAGPipeline
from ..core.config import settings
from .dependencies import get_rag_pipeline

router = APIRouter()

# Global variables (in production, use proper state management)
rag_pipeline: Optional[RAGPipeline] = None
processed_documents = []

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="rag-api"
    )

@router.post("/documents/upload", response_model=List[DocumentUploadResponse])
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents to the system"""
    try:
        uploaded_files = []
        
        for file in files:
            # Validate file type
            if file.content_type not in ['application/pdf', 'text/plain', 
                                       'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file.content_type}"
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{file_id}{file_extension}"
            file_path = f"storage/uploads/{unique_filename}"
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(DocumentUploadResponse(
                id=file_id,
                filename=file.filename,
                file_path=file_path,
                size=os.path.getsize(file_path),
                content_type=file.content_type,
                upload_timestamp=datetime.now().isoformat()
            ))
        
        return uploaded_files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/documents/process", response_model=ProcessDocumentsResponse)
async def process_documents(request: ProcessDocumentsRequest):
    """Process uploaded documents and create vector index"""
    global rag_pipeline, processed_documents
    
    try:
        if not request.api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Initialize components
        doc_processor = DocumentProcessor()
        vector_store = VectorStore(request.api_key)
        
        # Process documents
        all_chunks = []
        processed_files = []
        
        for file_id in request.file_ids:
            # Find file in uploads directory
            file_path = None
            for filename in os.listdir("storage/uploads"):
                if filename.startswith(file_id):
                    file_path = f"storage/uploads/{filename}"
                    break
            
            if not file_path or not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_id}")
            
            # Create a mock file object for processing
            class MockFile:
                def __init__(self, path):
                    self.name = os.path.basename(path)
                    self.path = path
                    # Determine content type from extension
                    ext = os.path.splitext(path)[1].lower()
                    if ext == '.pdf':
                        self.type = 'application/pdf'
                    elif ext == '.txt':
                        self.type = 'text/plain'
                    elif ext == '.docx':
                        self.type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    else:
                        self.type = 'application/octet-stream'
                
                def read(self):
                    with open(self.path, 'rb') as f:
                        return f.read()
                
                def seek(self, pos):
                    pass
            
            mock_file = MockFile(file_path)
            chunks = doc_processor.process_document(mock_file)
            all_chunks.extend(chunks)
            processed_files.append({
                "file_id": file_id,
                "filename": mock_file.name,
                "chunks_count": len(chunks)
            })
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="No text could be extracted from documents")
        
        # Create vector store
        vector_store.create_index(all_chunks)
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(vector_store=vector_store, api_key=request.api_key)
        processed_documents = all_chunks
        
        return ProcessDocumentsResponse(
            success=True,
            message=f"Successfully processed {len(all_chunks)} document chunks",
            total_chunks=len(all_chunks),
            processed_files=processed_files,
            processing_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the processed documents"""
    global rag_pipeline
    
    try:
        if rag_pipeline is None:
            raise HTTPException(
                status_code=400, 
                detail="No documents processed. Please upload and process documents first."
            )
        
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get response with sources
        result = rag_pipeline.get_response_with_sources(request.query, k=request.k)
        
        return QueryResponse(
            query=request.query,
            response=result["response"],
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
            num_sources=result.get("num_sources", 0),
            response_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/documents/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system statistics"""
    global rag_pipeline, processed_documents
    
    try:
        if rag_pipeline is None:
            return SystemStats(
                total_documents=0,
                total_chunks=0,
                embedding_dimension=0,
                index_size=0,
                memory_usage="0 MB",
                status="not_ready"
            )
        
        stats = rag_pipeline.get_pipeline_stats()
        
        return SystemStats(
            total_documents=len(processed_documents),
            total_chunks=stats["vector_store_stats"].get("total_documents", 0),
            embedding_dimension=stats["vector_store_stats"].get("embedding_dimension", 0),
            index_size=stats["vector_store_stats"].get("index_size", 0),
            memory_usage=stats["vector_store_stats"].get("memory_usage", "0 MB"),
            status="ready"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@router.delete("/documents/clear")
async def clear_documents():
    """Clear all processed documents and reset the system"""
    global rag_pipeline, processed_documents
    
    try:
        rag_pipeline = None
        processed_documents = []
        
        # Clear uploaded files
        upload_dir = "storage/uploads"
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        return {"message": "All documents cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

@router.get("/documents/similar-questions/{query}")
async def get_similar_questions(query: str, num_questions: int = 3):
    """Get similar questions based on the query"""
    global rag_pipeline
    
    try:
        if rag_pipeline is None:
            raise HTTPException(
                status_code=400, 
                detail="No documents processed. Please upload and process documents first."
            )
        
        questions = rag_pipeline.get_similar_questions(query, num_questions)
        
        return {
            "query": query,
            "similar_questions": questions,
            "count": len(questions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar questions failed: {str(e)}")
