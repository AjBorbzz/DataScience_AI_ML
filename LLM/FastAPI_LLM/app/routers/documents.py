from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.core.config import settings
from app.services import rag 


router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/process-document")
async def process_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    dest = settings.UPLOAD_DIR / file.filename
    content = await file.read()
    dest.write_bytes(content)

    chunks_added = rag.ingest_pdf(dest)
    return {"botResponse": f"PDF processed successfully. Indexed {chunks_added} chunks"}