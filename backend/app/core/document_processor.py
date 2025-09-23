# backend/app/core/document_processor.py
import PyPDF2
import docx
from typing import List
import re
import os

class DocumentProcessor:
    """Handles processing of different document types"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, file) -> List[str]:
        """Process uploaded document and return text chunks"""
        try:
            # Determine file type and extract text
            if hasattr(file, 'type'):
                file_type = file.type
            else:
                # Fallback to extension-based detection
                ext = os.path.splitext(file.name)[1].lower()
                type_map = {'.pdf': 'application/pdf', '.txt': 'text/plain', '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
                file_type = type_map.get(ext, 'unknown')
            
            if file_type == "application/pdf":
                text = self._extract_pdf_text(file)
            elif file_type == "text/plain":
                text = self._extract_txt_text(file)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = self._extract_docx_text(file)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Clean and chunk the text
            cleaned_text = self._clean_text(text)
            chunks = self._create_chunks(cleaned_text, file.name)
            
            return chunks
            
        except Exception as e:
            print(f"Error processing {file.name}: {str(e)}")
            return []
    
    def _extract_pdf_text(self, file) -> str:
        """Extract text from PDF file"""
        try:
            if hasattr(file, 'read'):
                # Handle file-like object
                pdf_reader = PyPDF2.PdfReader(file)
            else:
                # Handle file path
                with open(file.path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
            
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _extract_txt_text(self, file) -> str:
        """Extract text from TXT file"""
        try:
            if hasattr(file, 'read'):
                # Handle file-like object
                content = file.read()
                if isinstance(content, bytes):
                    # Try different encodings
                    encodings = ['utf-8', 'latin-1', 'cp1252']
                    for encoding in encodings:
                        try:
                            return content.decode(encoding)
                        except UnicodeDecodeError:
                            continue
                    raise Exception("Could not decode file with any supported encoding")
                else:
                    return content
            else:
                # Handle file path
                with open(file.path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    
    def _extract_docx_text(self, file) -> str:
        """Extract text from DOCX file"""
        try:
            if hasattr(file, 'read'):
                doc = docx.Document(file)
            else:
                doc = docx.Document(file.path)
            
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                    text += "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Error reading DOCX file: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:()\-"]', ' ', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    def _create_chunks(self, text: str, source_name: str) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end < len(text):
                sentence_end = text.rfind('.', start, end)
                if sentence_end != -1 and sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
                else:
                    word_end = text.rfind(' ', start, end)
                    if word_end != -1 and word_end > start + self.chunk_size // 2:
                        end = word_end
            
            chunk = text[start:end].strip()
            
            if chunk:
                chunk_with_metadata = f"[Source: {source_name}]\n{chunk}"
                chunks.append(chunk_with_metadata)
            
            start = end - self.chunk_overlap
            if start <= 0:
                start = end
        
        return chunks

# backend/app/core/vector_store.py
import google.generativeai as genai
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Tuple

class VectorStore:
    """Handles vector storage and retrieval using FAISS"""
    
    def __init__(self, api_key: str, embedding_dim: int = 384):
        self.api_key = api_key
        self.embedding_dim = embedding_dim
        self.index = None
        self.documents = []
        self.embeddings = []
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test API connection
        try:
            models = list(genai.list_models())
            if not models:
                raise Exception("No models available")
        except Exception as e:
            print(f"API key verification failed: {str(e)}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using TF-IDF"""
        try:
            return self._create_tfidf_embedding(text)
        except Exception as e:
            print(f"Error generating TF-IDF embedding: {str(e)}")
            return self._create_simple_embedding(text)
    
    def _create_tfidf_embedding(self, text: str) -> List[float]:
        """Create TF-IDF based embedding"""
        try:
            if not hasattr(self, '_tfidf_vectorizer'):
                print("TF-IDF vectorizer not initialized. Creating simple embedding...")
                return self._create_simple_embedding(text)
            
            vector = self._tfidf_vectorizer.transform([text]).toarray()[0]
            
            target_dim = 384
            if len(vector) < target_dim:
                vector = list(vector) + [0.0] * (target_dim - len(vector))
            elif len(vector) > target_dim:
                vector = vector[:target_dim]
            else:
                vector = list(vector)
            
            return vector
            
        except Exception as e:
            print(f"TF-IDF embedding failed: {str(e)}")
            return self._create_simple_embedding(text)
    
    def _create_simple_embedding(self, text: str) -> List[float]:
        """Create a simple hash-based embedding as fallback"""
        try:
            import hashlib
            
            text_bytes = text.encode('utf-8')
            embedding = []
            hash_funcs = [hashlib.md5, hashlib.sha1, hashlib.sha256]
            
            for i in range(self.embedding_dim):
                hash_func = hash_funcs[i % len(hash_funcs)]
                hash_input = f"{text}_{i}".encode('utf-8')
                hash_val = int(hash_func(hash_input).hexdigest()[:8], 16)
                normalized_val = (hash_val % 2000 - 1000) / 1000.0
                embedding.append(normalized_val)
            
            return embedding
            
        except Exception as e:
            print(f"Even simple embedding failed: {str(e)}")
            return [0.1] * self.embedding_dim
    
    def create_index(self, documents: List[str]) -> None:
        """Create FAISS index from documents"""
        try:
            if not documents:
                raise ValueError("No documents provided")
            
            if len(documents) < 2:
                print("Only one document chunk found. Adding padding for TF-IDF to work properly.")
                documents.extend([
                    "This is a padding document for TF-IDF processing.",
                    "Another padding document to ensure proper TF-IDF functionality."
                ])
            
            self.documents = documents
            self._initialize_tfidf_vectorizer(documents)
            
            embeddings = []
            for doc in documents:
                embedding = self.get_embedding(doc)
                embeddings.append(embedding)
            
            self.embeddings = np.array(embeddings, dtype='float32')
            
            if len(embeddings) > 0:
                self.embedding_dim = len(embeddings[0])
            
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            faiss.normalize_L2(self.embeddings)
            self.index.add(self.embeddings)
            
            print(f"Created FAISS index with {len(documents)} documents (embedding dim: {self.embedding_dim})")
            
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            raise
    
    def _initialize_tfidf_vectorizer(self, documents: List[str]) -> None:
        """Initialize TF-IDF vectorizer with all documents"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            self._tfidf_vectorizer = TfidfVectorizer(
                max_features=384,
                stop_words='english',
                lowercase=True,
                token_pattern=r'\b\w+\b',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95,
