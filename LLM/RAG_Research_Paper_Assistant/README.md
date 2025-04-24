Here’s a well-structured `README.md` for your RAG-powered research paper assistant app:

---

# 📚 RAG-powered Research Paper Assistant

A Streamlit-based app that leverages **Retrieval-Augmented Generation (RAG)** to help users explore and ask questions about research papers, either through **PDF uploads** or **arXiv search integration**.

This tool extracts content from uploaded PDFs or arXiv articles, semantically indexes the content using vector embeddings, and allows users to ask natural language questions. The app then uses a generative model (Gemini 1.5 Flash) to answer based on the context.

---

## ✨ Features

- 📄 Upload and process academic **PDFs**
- 🔍 Search and parse articles from **arXiv**
- 🔎 Perform **semantic search** using sentence embeddings
- 💬 Ask questions and receive AI-generated answers
- 🧠 Uses **SentenceTransformer** + **ChromaDB** for embeddings and vector storage
- 🧠 Powered by **Gemini 1.5 Flash** for context-aware response generation

---

## 🧰 Tech Stack

| Feature | Library |
|--------|--------|
| Web UI | [Streamlit](https://streamlit.io/) |
| PDF Parsing | [PyPDF2](https://pypi.org/project/PyPDF2/) |
| Embeddings | [SentenceTransformers](https://www.sbert.net/) |
| Vector DB | [ChromaDB](https://www.trychroma.com/) |
| RAG | [LiteLLM + Gemini](https://github.com/BerriAI/litellm) |
| Paper Search | [Langchain Arxiv Tool](https://python.langchain.com/) |
| Env Config | [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## 🚀 How It Works

### 1. **Upload PDFs**
- Upload multiple research papers.
- PDF content is extracted and chunked.
- Each chunk is embedded and stored in ChromaDB.
- Ask questions about the content.

### 2. **Search arXiv**
- Input a keyword/topic to search arXiv papers.
- Results are displayed and automatically processed into chunks.
- You can query the paper context directly.

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/research-paper-assistant.git
cd research-paper-assistant
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
GEMINI_API=your_gemini_api_key
HUGGING_FACE=your_huggingface_token
```

---

## ▶️ Running the App

```bash
streamlit run app.py
```

---

## 💡 Example Use Case

- Upload a research paper on deep learning.
- Ask: _“What is the main contribution of this paper?”_
- Get a contextually accurate summary powered by Gemini and semantic retrieval.

---

## 📝 Sample Screenshot

> _Add a screenshot here of your app running if available._

---

## 📌 To Do

- [ ] Add support for other academic databases (e.g., Semantic Scholar)
- [ ] Improve error handling on PDF extraction
- [ ] Enable file downloads of generated summaries

---
