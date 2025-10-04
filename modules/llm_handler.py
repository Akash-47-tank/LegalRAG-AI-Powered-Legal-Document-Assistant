"""
LLM Handler Module
Handles Groq API interactions for answer generation
"""

from groq import Groq
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handle LLM operations using Groq API"""
    
    def __init__(self, api_key: str, model: str = 'mixtral-8x7b-32768'):
        """
        Initialize LLM handler
        
        Args:
            api_key: Groq API key
            model: Model name to use
        """
        try:
            # Initialize Groq client without proxies parameter
            self.client = Groq(api_key=api_key)
            self.model = model
            logger.info(f"LLM Handler initialized with model: {model}")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {str(e)}")
            raise
    
    def generate_answer(self, query: str, context: str, sources: List[Dict]) -> Dict:
        """
        Generate answer using RAG
        
        Args:
            query: User query
            context: Retrieved context
            sources: Source documents
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Prepare prompt
            prompt = self._build_prompt(query, context)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a legal AI assistant specializing in analyzing legal documents. 
                        Provide accurate, well-reasoned answers based on the provided context. 
                        If the context doesn't contain enough information, clearly state that.
                        Always maintain a professional tone suitable for legal professionals.
                        Cite specific documents when making claims."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1024,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content
            
            logger.info("Successfully generated answer")
            
            return {
                'answer': answer,
                'sources': sources,
                'model': self.model,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                'answer': f"Error generating answer: {str(e)}",
                'sources': [],
                'model': self.model,
                'success': False
            }
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build RAG prompt
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Based on the following legal documents, please answer the question accurately and professionally.

CONTEXT:
{context}

QUESTION: {query}

INSTRUCTIONS:
- Provide a clear, concise answer based on the context
- Reference specific documents when applicable
- If the context doesn't contain sufficient information, state that clearly
- Use professional legal language
- Be factual and avoid speculation

ANSWER:"""
        
        return prompt
    
    def summarize_document(self, text: str, max_length: int = 200) -> str:
        """
        Summarize a document
        
        Args:
            text: Document text
            max_length: Maximum summary length
            
        Returns:
            Summary text
        """
        try:
            prompt = f"""Provide a concise summary of the following legal document:

{text[:4000]}  # Limit input text

Summary (in approximately {max_length} words):"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal document summarization expert. Provide clear, accurate summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content
            logger.info("Successfully generated summary")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing document: {str(e)}")
            return f"Error generating summary: {str(e)}"