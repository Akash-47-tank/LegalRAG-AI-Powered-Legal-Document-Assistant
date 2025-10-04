"""
Vector Store Module
Handles FAISS vector database operations
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for document embeddings"""
    
    def __init__(self, embedding_dimension: int, store_path: str):
        """
        Initialize vector store
        
        Args:
            embedding_dimension: Dimension of embeddings
            store_path: Path to save/load vector store
        """
        self.embedding_dimension = embedding_dimension
        self.store_path = store_path
        self.index_file = os.path.join(store_path, 'faiss_index.bin')
        self.metadata_file = os.path.join(store_path, 'metadata.pkl')
        
        # Initialize or load index
        if self.index_exists():
            self.load()
        else:
            self.index = faiss.IndexFlatL2(embedding_dimension)
            self.metadata = []
        
        logger.info(f"Vector store initialized with {self.index.ntotal} vectors")
    
    def index_exists(self) -> bool:
        """Check if index files exist"""
        return os.path.exists(self.index_file) and os.path.exists(self.metadata_file)
    
    def add_documents(self, embeddings: np.ndarray, metadata: List[Dict]):
        """
        Add documents to vector store
        
        Args:
            embeddings: Numpy array of embeddings
            metadata: List of metadata dictionaries
        """
        try:
            # Ensure embeddings are float32
            embeddings = embeddings.astype('float32')
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Store metadata
            self.metadata.extend(metadata)
            
            logger.info(f"Added {len(metadata)} documents. Total: {self.index.ntotal}")
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search(self, query_embedding: np.ndarray, k: int = 4) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (metadata, distance) tuples
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector store is empty")
                return []
            
            # Ensure query is 2D float32
            query_embedding = query_embedding.astype('float32').reshape(1, -1)
            
            # Search
            distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            
            # Prepare results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.metadata):
                    # Convert L2 distance to similarity score (0-1)
                    similarity = 1 / (1 + distance)
                    results.append((self.metadata[idx], similarity))
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
    
    def save(self):
        """Save index and metadata to disk"""
        try:
            os.makedirs(self.store_path, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, self.index_file)
            
            # Save metadata
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Vector store saved to {self.store_path}")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise
    
    def load(self):
        """Load index and metadata from disk"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_file)
            
            # Load metadata
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"Vector store loaded from {self.store_path}")
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise
    
    def clear(self):
        """Clear the vector store"""
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        self.metadata = []
        logger.info("Vector store cleared")
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.embedding_dimension,
            'total_documents': len(set(m.get('metadata', {}).get('source') for m in self.metadata))
        }