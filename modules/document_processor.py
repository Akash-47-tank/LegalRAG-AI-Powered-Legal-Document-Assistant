"""
Document Processing Module
Handles PDF, DOCX, and TXT file processing
"""

import os
from typing import List, Dict
from PyPDF2 import PdfReader
from docx import Document
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process various document formats and extract text"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF file with page numbers
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of dictionaries containing page text and metadata
        """
        try:
            reader = PdfReader(file_path)
            documents = []
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text.strip():
                    documents.append({
                        'text': text,
                        'metadata': {
                            'source': os.path.basename(file_path),
                            'page': page_num,
                            'type': 'pdf'
                        }
                    })
            
            logger.info(f"Extracted {len(documents)} pages from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from DOCX file
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            List of dictionaries containing text and metadata
        """
        try:
            doc = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            
            documents = [{
                'text': text,
                'metadata': {
                    'source': os.path.basename(file_path),
                    'type': 'docx'
                }
            }]
            
            logger.info(f"Extracted text from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing DOCX {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            List of dictionaries containing text and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            documents = [{
                'text': text,
                'metadata': {
                    'source': os.path.basename(file_path),
                    'type': 'txt'
                }
            }]
            
            logger.info(f"Extracted text from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing TXT {file_path}: {str(e)}")
            raise
    
    @classmethod
    def process_document(cls, file_path: str) -> List[Dict[str, any]]:
        """
        Process document based on file extension
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of processed document chunks
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return cls.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return cls.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return cls.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # At least 50% of chunk size
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
        
        return [c for c in chunks if c]  # Remove empty chunks