import streamlit as st
import os
import shutil
import time
from ingest import run_ingest
from qa import ask_question

# Configuration
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "documents")

# Page Config
st.set_page_config(
    page_title="AI Tra Cứu Tài Liệu (Offline)",
    page_icon="🤖",
    layout="wide"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.image("https://ollama.com/public/ollama.png", width=100) # Placeholder or local icon
    st.title("📂 Quản lý tài liệu")
    st.markdown("---")
    
    # File Uploader
    uploaded_files = st.file_uploader(
        "Tải lên tài liệu mới (PDF, DOCX, TXT)",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt"]
    )
    
    if uploaded_files:
        if st.button("Lưu & Xử lý ngay"):
            with st.status("Đang xử lý...", expanded=True) as status:
                # Ensure directory exists
                os.makedirs(DOCS_DIR, exist_ok=True)
                
                # Save Files
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(DOCS_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.write(f"✅ Đã lưu: {uploaded_file.name}")
                
                # Run Ingestion
                st.write("⏳ Đang tạo dữ liệu (Embedding)...")
                result_msg = run_ingest()
                st.write(f"ℹ️ {result_msg}")
                
                status.update(label="Hoàn tất!", state="complete", expanded=False)
            st.success("Đã cập nhật dữ liệu thành công!")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.caption("v1.0.0 | Chạy Local với Ollama")

# Main Interface
st.title("🤖 Trợ lý AI - Tra cứu Tài liệu")
st.markdown("""
Hệ thống trả lời câu hỏi dựa trên tài liệu **của bạn**.
Hoạt động hoàn toàn **Offline**, bảo mật & riêng tư.
""")

# Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Đặt câu hỏi về tài liệu của bạn..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate Answer
    with st.chat_message("assistant"):
        with st.spinner("AI đang đọc tài liệu để trả lời..."):
            response = ask_question(prompt)
            answer = response["answer"]
            sources = response["source_documents"]
            
            # Display Answer
            st.markdown(answer)
            
            # Show Sources (Optional but good for trust)
            if sources:
                with st.expander("📚 Nguồn thảm khảo"):
                    for i, doc in enumerate(sources):
                        st.markdown(f"**Nguồn {i+1}:** {os.path.basename(doc.metadata.get('source', 'Unknown'))} (Trang {doc.metadata.get('page', 'N/A')})")
                        st.text(doc.page_content[:200] + "...")

    # Save Assistant Message
    st.session_state.messages.append({"role": "assistant", "content": answer})
