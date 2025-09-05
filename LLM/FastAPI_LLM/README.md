# FastAPI RAG Chatbot (Private Llama3:8B)

This project provides a production-ready but minimal chatbot system built with FastAPI, designed to work with a private Large Language Model (LLM) such as Llama 3 8B. The chatbot can accept PDF uploads, extract and index their contents, and then answer questions by retrieving and summarizing information directly from those PDFs.

The purpose is to give developers, businesses, and learners a clear, working foundation to build RAG (Retrieval-Augmented Generation) applications in a private and secure environment, without depending on external cloud services.

### Why It Matters

- **Data Privacy**: Many organizations cannot share internal data with external APIs. Running Llama 3 locally (via Ollama or llama.cpp) ensures sensitive documents stay private.

- **Control**: No vendor lock-in. You can run your own models, use your own embeddings, and fully own your infrastructure.

- **Scalability**: Built with FastAPI, the system is ready for production deployment with Docker, reverse proxies, and cloud scaling.

- **Simplicity**: Avoids unnecessary dependencies while still being extensible. You can use it as a template for future AI applications.

### Best Use Cases

1. **Enterprise Knowledge Bots**: Employees upload contracts, manuals, or reports and query them without exposing documents to external services.

2. **Academic and Research Assistants**: Students or researchers upload papers and ask questions across multiple documents.

3. **Customer Support**: Support teams upload product documentation and use the chatbot to quickly answer client queries.

4. **Legal and Compliance**: Securely query sensitive legal agreements, compliance documents, or internal policies.

### Functionality

- PDF Ingestion: Uploads PDF files, extracts text, splits into chunks, embeds them, and stores them in a FAISS vector index.

- RAG (Retrieval-Augmented Generation): Retrieves the most relevant document sections to enrich chatbot answers.

- Private LLM Integration: Works with Llama 3 8B locally using either Ollama or llama.cpp.

- FastAPI-based API: Provides endpoints for PDF upload and chat, accessible via curl, Postman, or frontend apps.

- Persistence: Indexed data is stored locally, making documents queryable across sessions.

### Audience

This README is written for a broad audience:

* Sales & Business Teams: Understand that this project allows building chatbots over company data without leaking information.

* Non-Technical Users: Upload PDFs, ask natural language questions, and get reliable answers directly from the documents.

* Technical Teams (Developers, Data Engineers, ML Engineers): Use the FastAPI scaffold to extend the system with authentication, analytics, or integrations.

* Computer Science Students & Beginners: Learn how Retrieval-Augmented Generation works by studying a clean, minimal example.

### How It Works

User uploads a PDF → stored locally and indexed with embeddings.

User asks a question → system retrieves relevant text chunks from the PDF.

Context is passed to the private Llama 3 model → chatbot responds with an answer grounded in the uploaded document.

### Example Workflow

Upload a contract PDF with:

```curl -F "file=@contract.pdf" http://localhost:8000/api/documents/process-document```

### Ask a question about it:

```bash
curl -H "Content-Type: application/json" \
     -d '{"userMessage": "What are the payment terms?"}' \
     http://localhost:8000/api/chat/process-message
```

Receive a contextual answer generated only from the uploaded PDF.

### Key Takeaway

This project is your blueprint for building private, document-aware chatbots using modern LLMs. It balances simplicity and production-readiness, making it useful as a starting point for enterprise, research, and personal AI projects.