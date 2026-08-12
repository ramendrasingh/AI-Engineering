from pydantic import BaseModel, Field
from typing import List

class GenerateRequest(BaseModel):
    user_id: str
    prompt: str


class GenerateResponse(BaseModel):
    response: str

class ChatMessage(BaseModel):
    role: str
    content: str   
     
class ConversationState(BaseModel):
    summary: str = ""
    messages: List[ChatMessage] = Field(default_factory=list)