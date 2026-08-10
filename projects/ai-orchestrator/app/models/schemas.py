from pydantic import BaseModel

class GenerateRequest(BaseModel):
    user_id: str
    prompt: str


class GenerateResponse(BaseModel):
    response: str

class UserMessage(BaseModel):
    role: str
    content: str    