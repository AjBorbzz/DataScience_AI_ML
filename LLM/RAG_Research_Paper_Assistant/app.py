import os
import sys
import hashlib
import PyPDF2
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import login
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.tools import ArxivQueryRun
import chromadb
from litellm import completion

# Fix for torch.classes error
sys.modules['torch.classes'].__path__ = []

# Load environment variables
load_dotenv()
gemini_api = os.getenv("GEMINI_API")
hugging_face = os.getenv("HUGGING_FACE")

# Hugging Face login
if hugging_face:
    login(token=hugging_face)

# Global objects
@st.cache_resource

def get_chroma_client():
    return chromadb.PersistentClient(path="chroma_db")

@st.cache_resource

def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

client = get_chroma_client()
text_embedding_model = get_embedding_model()
arxiv_tool = ArxivQueryRun()

# ---------- PDF & Text Processing ----------
def extract_text_from_pdfs(uploaded_files):
    all_text = ""
    for uploaded_file in uploaded_files:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            all_text += page.extract_text() or ""
    return all_text

def process_text_and_store(all_text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(all_text)

    try:
        client.delete_collection(name="knowledge_base")
    except Exception:
        pass

    collection = client.create_collection(name="knowledge_base")

    for i, chunk in enumerate(chunks):
        embedding = text_embedding_model.encode(chunk)
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding.tolist()],
            metadatas=[{"source": "pdf", "chunk_id": i}],
            documents=[chunk]
        )
    return collection

# ✅ Cached version
@st.cache_resource
def process_text_and_store_cached(text_hash, all_text):
    return process_text_and_store(all_text)

# ---------- Semantic Search & Completion ----------
def semantic_search(query, collection, top_k=2):
    query_embedding = text_embedding_model.encode(query)
    results = collection.query(
        query_embeddings=[query_embedding.tolist()], n_results=top_k
    )
    return results

def generate_response(query, context):
    prompt = f"Query: {query}\nContext: {context}\nAnswer: "
    response = completion(
        model="gemini/gemini-1.5-flash",
        messages=[{"content": prompt, "role": "user"}],
        api_key=gemini_api
    )
    return response['choices'][0]['message']['content']

# ---------- Cached Query Execution ----------
def execute_query_frm_input(query, collection):
    results = semantic_search(query, collection)
    context = "\n".join(results['documents'][0])
    response = generate_response(query, context)
    st.subheader("Generated Response:")
    st.write(response)

# ---------- Main Streamlit UI ----------
def main():
    st.title("RAG-powered Research Paper Assistant")
    st.sidebar.write("## Upload and download :gear:")

    option = st.sidebar.radio("Choose an option", ("Upload PDFs", "Search arXiv"))

    with st.sidebar.expander("ℹ️ PDF Guidelines"):
        st.write("""
        - Upload arXiv article/publication
        - Large images will be automatically resized
        - Supported formats: PDF
        - Processing time depends on file size
        """)

    if option == "Upload PDFs":
        uploaded_files = st.sidebar.file_uploader("Upload PDF Files", accept_multiple_files=True, type=["pdf"])
        if uploaded_files:
            st.write("Processing uploaded files...")
            all_text = extract_text_from_pdfs(uploaded_files)

            # ✅ Generate hash and use cached version
            text_hash = hashlib.md5(all_text.encode()).hexdigest()
            collection = process_text_and_store_cached(text_hash, all_text)

            st.success("PDF content processed and stored successfully!")

            query = st.text_input("Enter your query: ")
            if st.button("Execute Query") and query:
                execute_query_frm_input(query, collection)

    elif option == "Search arXiv":
        query = st.text_input("Enter your search query for arXiv:")

        if st.button("Search ArXiv") and query:
            arxiv_results = arxiv_tool.invoke(query)
            st.session_state["arxiv_results"] = arxiv_results
            st.subheader("Search Results:")
            st.write(arxiv_results)

            collection = process_text_and_store(arxiv_results)
            st.session_state["collection"] = collection
            st.success("arXiv paper content processed and stored successfully!")

        if "arxiv_results" in st.session_state and "collection" in st.session_state:
            query = st.text_input("Ask a question about the paper:")
            if st.button("Execute Query on Paper") and query:
                results = semantic_search(query, st.session_state["collection"])
                context = "\n".join(results['documents'][0])
                response = generate_response(query, context)
                st.subheader("Generated Response:")
                st.write(response)

if __name__ == "__main__":
    main()
