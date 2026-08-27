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
    arguments: dict[str, Any] = Field(default_factory=lambda: {"": None})


class ConversationContext(BaseModel):
    conversation_id: str
    role: str
    user_message: str
    conversation_history: list[ChatMessage]
    latest_messages: list[ChatMessage]
    summary: str = ""
    system_message: ChatMessage
    current_message: ChatMessage


class SearchFilesArguments(BaseModel):
    query: str = Field(min_length=1)


class ReadFileArguments(BaseModel):
    path: str = Field(min_length=1)


class ListDirectoryArguments(BaseModel):
    path: str = "."
