"""
Retriever Module
Handles document retrieval and context preparation
"""

from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Retrieve relevant documents based on query"""
    
    def __init__(self, vector_store, embedding_generator, top_k: int = 4, threshold: float = 0.5):
        """
        Initialize retriever
        
        Args:
            vector_store: Vector store instance
            embedding_generator: Embedding generator instance
            top_k: Number of documents to retrieve
            threshold: Similarity threshold
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.top_k = top_k
        self.threshold = threshold
    
    def retrieve(self, query: str) -> List[Tuple[Dict, float]]:
        """
        Retrieve relevant documents for query
        
        Args:
            query: User query
            
        Returns:
            List of (document_data, similarity_score) tuples
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Search vector store
            results = self.vector_store.search(query_embedding, k=self.top_k)
            
            # Filter by threshold
            filtered_results = [(doc, score) for doc, score in results if score >= self.threshold]
            
            logger.info(f"Retrieved {len(filtered_results)} documents above threshold {self.threshold}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    def prepare_context(self, retrieved_docs: List[Tuple[Dict, float]]) -> Tuple[str, List[Dict]]:
        """
        Prepare context for LLM from retrieved documents
        
        Args:
            retrieved_docs: List of retrieved documents with scores
            
        Returns:
            Tuple of (context_string, source_list)
        """
        if not retrieved_docs:
            return "", []
        
        context_parts = []
        sources = []
        
        for idx, (doc, score) in enumerate(retrieved_docs, 1):
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            
            # Build context
            context_parts.append(f"[Document {idx}]\n{text}\n")
            
            # Build source reference
            sources.append({
                'document': metadata.get('source', 'Unknown'),
                'page': metadata.get('page'),
                'relevance': round(score, 2),
                'type': metadata.get('type', 'unknown')
            })
        
        context = "\n".join(context_parts)
        logger.info(f"Prepared context with {len(retrieved_docs)} documents")
        
        return context, sources