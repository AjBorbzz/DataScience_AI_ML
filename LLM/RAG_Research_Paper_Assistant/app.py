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


def main():
    pass

if __name__ == "__main__":
    main()