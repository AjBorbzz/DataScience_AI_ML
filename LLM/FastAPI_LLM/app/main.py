from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.core.logging import configure_logging 
from app.routers import chat, documents 


configure_logging()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(documents.router, prefix=settings.API_PREFIX)

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html><head><title>FastAPI RAG Chatbot</title></head>
    <body>
    <h1>FastAPI RAG Chatbot</h1>
    <p>POST /api/documents/process-document (multipart: file=pdf)</p>
    <p>POST /api/chat/process-message (json: {"userMessage": "..."})</p>
    </body></html>
    """