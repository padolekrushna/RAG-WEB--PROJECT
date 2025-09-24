# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional
import os
import time
from .api.routes import router
from .core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_time = time.time()
    print("🚀 Starting RAG Document Q&A API...")
    
    # Create necessary directories
    os.makedirs("storage/uploads", exist_ok=True)
    os.makedirs("storage/indexes", exist_ok=True)
    os.makedirs("storage/logs", exist_ok=True)
    
    elapsed = time.time() - start_time
    print(f"✅ Server startup completed in {elapsed:.2f} seconds")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting RAG Document Q&A API...")
    
    # Create necessary directories
    os.makedirs("storage/uploads", exist_ok=True)
    os.makedirs("storage/indexes", exist_ok=True)
    os.makedirs("storage/logs", exist_ok=True)
    
    yield
    
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="RAG Document Q&A API",
    description="API for RAG-based document question answering system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "RAG Document Q&A API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-api"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
