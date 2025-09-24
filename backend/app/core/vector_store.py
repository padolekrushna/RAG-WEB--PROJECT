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
        self._tfidf_vectorizer = None  # Initialize as None — will be created later
        
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
        """Get embedding for text using TF-IDF or fallback"""
        try:
            if self._tfidf_vectorizer is not None:
                return self._create_tfidf_embedding(text)
            else:
                print("⚠️ TF-IDF vectorizer not initialized. Using simple embedding.")
                return self._create_simple_embedding(text)
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return self._create_simple_embedding(text)

    def _create_tfidf_embedding(self, text: str) -> List[float]:
        """Create TF-IDF based embedding"""
        try:
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
            
            
            
            self.documents = documents
            self._initialize_tfidf_vectorizer(documents)  # ✅ Initialize here — inside method!
            
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
            
            print(f"✅ Created FAISS index with {len(documents)} documents (embedding dim: {self.embedding_dim})")
            
        except Exception as e:
            print(f"❌ Error creating index: {str(e)}")
            raise

    def _initialize_tfidf_vectorizer(self, documents: List[str]) -> None:
        """
        Initialize TF-IDF vectorizer with the provided documents.
        This creates a vocabulary and IDF weights based on the corpus.
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            # Initialize TF-IDF Vectorizer with robust settings
            self._tfidf_vectorizer = TfidfVectorizer(
                max_features=384,               # Limit to top 384 features
                stop_words='english',           # Remove common English stop words
                lowercase=True,                 # Convert all text to lowercase
                token_pattern=r'\b\w+\b',       # Tokenize by word boundaries
                ngram_range=(1, 2),             # Use unigrams and bigrams
                min_df=1,                       # Include terms in at least 1 doc
                max_df=0.95                     # Ignore terms in >95% of docs
            )

            # Fit the vectorizer on the documents
            self._tfidf_vectorizer.fit(documents)
            print(f"✅ TF-IDF vectorizer initialized with {len(self._tfidf_vectorizer.vocabulary_)} terms.")

        except ImportError:
            print("⚠️ scikit-learn not installed. TF-IDF vectorizer will not be available.")
            self._tfidf_vectorizer = None
        except Exception as e:
            print(f"❌ Failed to initialize TF-IDF vectorizer: {str(e)}")
            self._tfidf_vectorizer = None

            
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for similar documents and return structured results"""
        if self.index is None:
            return []

        try:
            query_embedding = np.array([self.get_embedding(query)], dtype='float32')
            faiss.normalize_L2(query_embedding)
            distances, indices = self.index.search(query_embedding, k)

            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx >= len(self.documents):
                    continue

                doc_text = self.documents[idx]
                
                # ❌ SKIP PADDING DOCUMENTS
                if "padding document for TF-IDF" in doc_text:
                    continue

                source_name = "Unknown"
                preview_text = doc_text

                # Extract source name if present in format [Source: ...]
                if doc_text.startswith("[Source:"):
                    end_bracket = doc_text.find("]\n")
                    if end_bracket != -1:
                        source_name = doc_text[8:end_bracket]  # Extract "filename.pdf"
                        preview_text = doc_text[end_bracket + 2:]  # Text after the header

                # Create structured source object
                results.append({
                    "chunk_id": i + 1,
                    "source_name": source_name,
                    "similarity_score": float(distances[0][i]),
                    "preview": preview_text[:300] + "..." if len(preview_text) > 300 else preview_text
                })

                # Stop if we have enough real results
                if len(results) >= k:
                    break

            return results

        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []