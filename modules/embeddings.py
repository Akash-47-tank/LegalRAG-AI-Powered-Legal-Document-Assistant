"""
Embeddings Module
Handles document embeddings using HuggingFace models
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging
import torch

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using HuggingFace sentence transformers"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize embedding model
        
        Args:
            model_name: HuggingFace model name
        """
        logger.info(f"Loading embedding model: {model_name}")
        
        # Optimize for M1 Mac
        device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        logger.info(f"Using device: {device}")
        
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dimension}")
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string
            
        Returns:
            Numpy array embedding
        """
        return self.model.encode([text], convert_to_numpy=True)[0]