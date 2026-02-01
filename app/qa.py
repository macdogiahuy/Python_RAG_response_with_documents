import os
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from retriever import get_vector_store

# Configuration
LLM_MODEL = "llama3.2:1b"
# Threshold for similarity search (0.0 to 1.0). 
# Higher = stricter. 
SIMILARITY_THRESHOLD = 0.7 

def format_docs(docs):
    """Format documents for the prompt, including citation info."""
    formatted_docs = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        # Extract filename only
        filename = os.path.basename(source)
        page = doc.metadata.get("page", "N/A")
        content = doc.page_content.replace("\n", " ")
        formatted_docs.append(f"CONTENT: {content}\nSOURCE: {filename} (Trang {page})\n")
    return "\n---\n".join(formatted_docs)

def get_strict_prompt():
    """Define a strictly constrained prompt."""
    template = """SYSTEM:
Bạn là một trợ lý AI chuyên nghiệp về tra cứu tài liệu (RAG).
NHIỆM VỤ: Trả lời câu hỏi của người dùng CHỈ dựa trên thông tin được cung cấp trong phần CONTEXT bên dưới.

QUY TẮC BẮT BUỘC:
1. TUYỆT ĐỐI KHÔNG sử dụng kiến thức bên ngoài. Nếu thông tin không có trong Context, KHÔNG được bịa ra.
2. Nếu Context không chứa câu trả lời, hãy trả lời chính xác: "Không tìm thấy thông tin liên quan trong tài liệu được cung cấp."
3. BẮT BUỘC trích dẫn nguồn ở cuối câu trả lời (Ví dụ: [Nguồn: ten_file.pdf, Trang 1]).
4. Trả lời bằng Tiếng Việt.

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

def ask_question(question: str):
    """
    Execute the RAG pipeline with strict checks.
    1. Retrieve docs with score threshold.
    2. Check if docs are empty.
    3. If empty -> Return fallback.
    4. If not empty -> Generate answer.
    """
    try:
        # 1. Initialize Components
        vector_store = get_vector_store()
        
        # 2. Retrieval with Score Filtering
        # similarity_search_with_relevance_scores normalizes scores (usually 0-1)
        # Note: If using Chroma default L2, this wrapper converts it to a relevance score.
        results = vector_store.similarity_search_with_relevance_scores(question, k=5)
        
        # 3. Filter by Threshold
        filtered_docs = []
        if results:
            filtered_docs = [doc for doc, score in results if score >= SIMILARITY_THRESHOLD]
            
            # Debug info
            print(f"DEBUG: Found {len(results)} docs. After threshold {SIMILARITY_THRESHOLD}: {len(filtered_docs)} docs.")
            for doc, score in results:
                print(f" - Score: {score:.4f} | Src: {os.path.basename(doc.metadata.get('source', ''))}")
        else:
            print("DEBUG: No documents found by vector store.")

        # 4. Fallback if no relevant documents found
        if not filtered_docs:
            return {
                "answer": "Không tìm thấy thông tin liên quan trong tài liệu được cung cấp (Không đủ độ tin cậy).",
                "source_documents": []
            }

        # 5. Generation
        llm = Ollama(model=LLM_MODEL, temperature=0.0) # Zero temp for strictness
        prompt_template = get_strict_prompt()
        
        # Prepare context
        context_text = format_docs(filtered_docs)
        prompt = prompt_template.format(context=context_text, question=question)
        
        # Invoke LLM
        answer = llm.invoke(prompt)
        
        # 6. Return Result
        return {
            "answer": answer,
            "source_documents": filtered_docs
        }

    except Exception as e:
        print(f"ERROR in ask_question: {e}")
        return {
            "answer": f"Đã xảy ra lỗi hệ thống: {str(e)}",
            "source_documents": []
        }
