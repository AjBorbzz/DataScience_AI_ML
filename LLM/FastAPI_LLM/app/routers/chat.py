from fastapi import APIRouter
from app.models.schemas import MessageIn, MessageOut
from app.services import rag
from app.services.llm import get_llm 


router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/process-message", response_model=MessageOut)
async def process_message(payload: MessageIn) -> MessageOut:
    llm = get_llm()
    results = rag.retrieve(payload.userMessage)
    contexts = [c for c, _ in results]
    messages = rag.build_prompt(payload.userMessage, contexts)
    answer = llm.chat(messages, max_tokens=512)
    return MessageOut(botResponse=answer)



