from pydantic import BaseModel


class MessageIn(BaseModel):
    userMessage: str


class MessageOut(BaseModel):
    botResponse: str