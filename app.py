"""
LegalRAG - Main Flask Application
AI-Powered Legal Document Assistant using RAG
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from typing import List

from config import Config
from modules import (
    DocumentProcessor,
    EmbeddingGenerator,
    VectorStore,
    DocumentRetriever,
    LLMHandler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize directories
Config.init_app()

# Global instances (initialized on first use)
embedding_generator = None
vector_store = None
document_retriever = None
llm_handler = None


def initialize_models():
    """Initialize all models and components (lazy loading)"""
    global embedding_generator, vector_store, document_retriever, llm_handler
    
    if embedding_generator is None:
        logger.info("Initializing models...")
        
        # Initialize embedding generator
        embedding_generator = EmbeddingGenerator(Config.EMBEDDING_MODEL)
        
        # Initialize vector store
        vector_store = VectorStore(
            embedding_dimension=embedding_generator.embedding_dimension,
            store_path=Config.VECTOR_STORE_PATH
        )
        
        # Initialize retriever
        document_retriever = DocumentRetriever(
            vector_store=vector_store,
            embedding_generator=embedding_generator,
            top_k=Config.TOP_K_DOCUMENTS,
            threshold=Config.SIMILARITY_THRESHOLD
        )
        
        # Initialize LLM handler with detailed logging
        if not Config.GROQ_API_KEY:
            logger.error("=" * 80)
            logger.error("GROQ_API_KEY NOT FOUND!")
            logger.error("Please add your Groq API key to the .env file:")
            logger.error("GROQ_API_KEY=gsk_your_key_here")
            logger.error("Get a free key at: https://console.groq.com/keys")
            logger.error("=" * 80)
        else:
            try:
                logger.info(f"Initializing LLM Handler with key: {Config.GROQ_API_KEY[:10]}...")
                llm_handler = LLMHandler(
                    api_key=Config.GROQ_API_KEY,
                    model=Config.GROQ_MODEL
                )
                logger.info("✓ LLM Handler initialized successfully!")
            except Exception as e:
                logger.error(f"✗ Failed to initialize LLM Handler: {str(e)}")
                logger.error("Query features will not work without LLM!")
        
        logger.info("Models initialized successfully")


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': embedding_generator is not None
    })


@app.route('/api/upload', methods=['POST'])
def upload_documents():
    """
    Upload and process documents
    
    Returns:
        JSON response with upload status
    """
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_files = []
        processed_count = 0
        
        # Process each file
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filename)
                processed_count += 1
        
        if processed_count == 0:
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        return jsonify({
            'message': f'Successfully uploaded {processed_count} document(s)',
            'files': uploaded_files,
            'count': processed_count
        })
        
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/index', methods=['POST'])
def index_documents():
    """
    Index uploaded documents into vector store
    
    Returns:
        JSON response with indexing status
    """
    try:
        # Initialize models if needed
        initialize_models()
        
        # Get list of uploaded files
        upload_folder = app.config['UPLOAD_FOLDER']
        files = [f for f in os.listdir(upload_folder) if allowed_file(f)]
        
        if not files:
            return jsonify({'error': 'No documents to index'}), 400
        
        total_chunks = 0
        indexed_files = []
        
        # Process each document
        for filename in files:
            filepath = os.path.join(upload_folder, filename)
            
            # Extract text
            documents = DocumentProcessor.process_document(filepath)
            
            # Chunk documents
            chunks = []
            chunk_metadata = []
            
            for doc in documents:
                text_chunks = DocumentProcessor.chunk_text(
                    doc['text'],
                    chunk_size=Config.CHUNK_SIZE,
                    chunk_overlap=Config.CHUNK_OVERLAP
                )
                
                for chunk in text_chunks:
                    chunks.append(chunk)
                    chunk_metadata.append({
                        'text': chunk,
                        'metadata': doc['metadata']
                    })
            
            # Generate embeddings
            embeddings = embedding_generator.generate_embeddings(chunks)
            
            # Add to vector store
            vector_store.add_documents(embeddings, chunk_metadata)
            
            total_chunks += len(chunks)
            indexed_files.append(filename)
        
        # Save vector store
        vector_store.save()
        
        return jsonify({
            'message': f'Successfully indexed {len(indexed_files)} document(s)',
            'files': indexed_files,
            'total_chunks': total_chunks,
            'stats': vector_store.get_stats()
        })
        
    except Exception as e:
        logger.error(f"Error indexing documents: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/query', methods=['POST'])
@app.route('/api/query', methods=['POST'])
def query_documents():
    """
    Query indexed documents
    
    Returns:
        JSON response with answer and sources
    """
    try:
        # Initialize models if needed
        initialize_models()
        
        # Get query from request
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Check if documents are indexed
        if vector_store is None or vector_store.index.ntotal == 0:
            return jsonify({'error': 'No documents indexed. Please upload and index documents first.'}), 400
        
        # Check if LLM is available
        if llm_handler is None:
            return jsonify({
                'error': 'LLM not configured. Please set GROQ_API_KEY in .env file',
                'help': 'Get a free API key at https://console.groq.com'
            }), 500
        
        # Retrieve relevant documents
        retrieved_docs = document_retriever.retrieve(query)
        
        if not retrieved_docs:
            return jsonify({
                'answer': 'I could not find any relevant information in the indexed documents to answer your question.',
                'sources': [],
                'query': query
            })
        
        # Prepare context
        context, sources = document_retriever.prepare_context(retrieved_docs)
        
        # Generate answer
        result = llm_handler.generate_answer(query, context, sources)
        
        return jsonify({
            'answer': result['answer'],
            'sources': result['sources'],
            'query': query,
            'model': result['model']
        })
        
    except Exception as e:
        logger.error(f"Error querying documents: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_database():
    """
    Clear vector store and uploaded files
    
    Returns:
        JSON response with clear status
    """
    try:
        # Clear vector store
        if vector_store is not None:
            vector_store.clear()
            vector_store.save()
        
        # Clear uploaded files
        upload_folder = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(upload_folder):
            filepath = os.path.join(upload_folder, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        
        return jsonify({
            'message': 'Successfully cleared all data',
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics
    
    Returns:
        JSON response with statistics
    """
    try:
        if vector_store is None:
            return jsonify({
                'indexed': False,
                'stats': {}
            })
        
        stats = vector_store.get_stats()
        
        # Get uploaded files count
        upload_folder = app.config['UPLOAD_FOLDER']
        uploaded_files = len([f for f in os.listdir(upload_folder) if allowed_file(f)])
        
        return jsonify({
            'indexed': True,
            'stats': stats,
            'uploaded_files': uploaded_files
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)