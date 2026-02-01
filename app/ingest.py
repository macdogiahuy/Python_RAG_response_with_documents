import os
import glob
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from retriever import get_vector_store

# Configuration
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "documents")

def load_documents() -> List:
    """Load documents from the data/documents directory."""
    documents = []
    
    # Load PDFs
    for file_path in glob.glob(os.path.join(DOCS_DIR, "*.pdf")):
        try:
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
            print(f"Loaded PDF: {file_path}")
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")

    # Load Word Docs
    for file_path in glob.glob(os.path.join(DOCS_DIR, "*.docx")):
        try:
            loader = Docx2txtLoader(file_path)
            documents.extend(loader.load())
            print(f"Loaded DOCX: {file_path}")
        except Exception as e:
            print(f"Error loading DOCX {file_path}: {e}")

    # Load Text Files
    for file_path in glob.glob(os.path.join(DOCS_DIR, "*.txt")):
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())
            print(f"Loaded TXT: {file_path}")
        except Exception as e:
            print(f"Error loading TXT {file_path}: {e}")

    return documents

def split_documents(documents: List) -> List:
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_documents(documents)

def run_ingest():
    """Main ingestion function."""
    print(f"Scanning directory: {DOCS_DIR}")
    documents = load_documents()
    if not documents:
        print("No documents found.")
        return "Không tìm thấy tài liệu nào trong thư mục data/documents."
    
    print(f"Loaded {len(documents)} documents.")
    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    
    print("Creating vector database... This might take a while.")
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    vector_store.persist()
    print(f"Vector database updated with {len(chunks)} chunks.")
    
    return f"Đã xử lý xong {len(documents)} tài liệu và tạo {len(chunks)} đoạn dữ liệu."

if __name__ == "__main__":
    run_ingest()
