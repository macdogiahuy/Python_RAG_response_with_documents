from langchain_community.embeddings import OllamaEmbeddings

# Configuration
EMBEDDING_MODEL = "nomic-embed-text"

def get_embedding_function():
    """Return the Ollama embedding function."""
    return OllamaEmbeddings(model=EMBEDDING_MODEL)
