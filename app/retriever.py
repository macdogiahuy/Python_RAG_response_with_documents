import os
from langchain_community.vectorstores import Chroma
from embeddings import get_embedding_function

# Configuration
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vectordb")

def get_vector_store():
    """Return the ChromaDB vector store."""
    embedding_function = get_embedding_function()
    
    # Ensure directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Load or create ChromaDB
    vector_store = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embedding_function
    )
    return vector_store
