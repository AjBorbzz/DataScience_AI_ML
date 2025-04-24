import os
import PyPDF2
import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from litellm import completion
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.tools import ArxivQueryRun
from dotenv import load_dotenv
from huggingface_hub import login


load_dotenv()
gemini_api = os.getenv("GEMINI_API")
hugging_face=os.getenv("HUGGING_FACE")

if hugging_face:
    login(token=hugging_face)

client = chromadb.PersistentClient(path="chroma_db")
text_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
arxiv_tool = ArxivQueryRun()

def extract_text_from_pdfs(uploaded_files):
    all_text = ""
    for uploaded_file in uploaded_files:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            all_text += page.extract_text() or ""
    return all_text

def process_text_and_store(all_text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n","\n"," ", ""])
    chunks = text_splitter.split_text(all_text)
    try:
        client.delete_collection(name="knowledge_base")
    except Exception:
        pass

    collection = client.create_collection(name="knowledge_base")

    for i,chunk in enumerate(chunks):
        embedding = text_embedding_model.encode(chunk)
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding.tolist()]
            metadata=[{"source": "pdf", "chunk_id": i}],
            documents=[chunk]
        )
    return collection

def semantic_search(query, collection, top_k=2):
    query_embedding = text_embedding_model.encode(query)
    results = collection.query(
        query_embedding=[query_embedding.tolist()], n_results=top_k
    )
    return results

def generate_response(query, context):
    prompt = f"Query: {query}\nContext: {context}\nAnswer: "
    response = completion(
        model="gemini/gemini-1.5-flash",
        messages=[{"content": prompt, "role": "user"}]
        api_key=gemini_api
    )
    return response['choices'][0]['message']['content']


def main():
    st.title("RAG-powered Research Paper Assistant")
    option = st.radio("Choose an option", ("Upload PDFs", "Search arXiv"))
    if option == "Upload PDFs":
        uploaded_files = st.file_uploader("Upload PDF Files", accept_multiple_files=True, type=["pdf"])
        if uploaded_files:
            st.write("Processing uploaded files...")
            all_text = extract_text_from_pdfs(uploaded_files)
            collection = process_text_and_store(all_text)
            st.success("PDF content processed and stored successfully!")
    

if __name__ == "__main__":
    main()