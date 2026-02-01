from langchain_community.llms import Ollama
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from retriever import get_vector_store

# Configuration
LLM_MODEL = "llama3.2:1b" # Optimized for lower memory usage

def get_qa_chain():
    """Create the QA chain."""
    
    # Initialize LLM
    llm = Ollama(model=LLM_MODEL)
    
    # Initialize Vector Store Retriever
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 7} # Increase retrieval headers
    )
    
    # Define Prompt Template
    template = """SYSTEM:
Bạn là một trợ lý AI thông minh, nhiệm vụ của bạn là trả lời câu hỏi dựa trên các đoạn văn bản được cung cấp bên dưới (Context).
- Trả lời bằng Tiếng Việt, chi tiết và chính xác theo thông tin trong văn bản.
- KHÔNG sử dụng kiến thức bên ngoài, chỉ dùng thông tin từ Context.
- Nếu không tìm thấy câu trả lời trong Context, hãy nói rõ: "Tôi không tìm thấy thông tin này trong tài liệu được cung cấp."

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""
    
    PROMPT = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    
    # Create Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    return qa_chain

def ask_question(question: str):
    """Ask a question to the system."""
    qa_chain = get_qa_chain()
    
    try:
        response = qa_chain.invoke({"query": question})
        
        # Debug: Print retrieved docs
        print(f"DEBUG: Retrieval found {len(response['source_documents'])} docs.")
        for i, doc in enumerate(response['source_documents']):
            print(f"Doc {i}: {doc.page_content[:100]}...")
            
        return {
            "answer": response["result"],
            "source_documents": response["source_documents"]
        }
    except Exception as e:
        return {
            "answer": f"Lỗi khi xử lý câu hỏi: {str(e)}",
            "source_documents": []
        }
