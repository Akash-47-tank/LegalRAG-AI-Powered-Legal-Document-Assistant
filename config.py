import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    
    # Vector store settings
    VECTOR_STORE_PATH = 'data/vector_store'
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Model settings
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'  # Fast & efficient for M1
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')  # Latest Groq model
    
    # Retrieval settings
    TOP_K_DOCUMENTS = 4
    SIMILARITY_THRESHOLD = 0.5
    
    @staticmethod
    def init_app():
        """Initialize application directories"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)