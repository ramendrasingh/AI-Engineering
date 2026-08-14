from typing import Any

from pydantic import BaseModel, Field


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
    messages: list[ChatMessage] = Field(default_factory=list)


class ToolResult(BaseModel):
    success: bool
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ToolCall(BaseModel):
    tool: str | None = None
    arguments: dict[str, Any] = Field(default_factory={"": None})
