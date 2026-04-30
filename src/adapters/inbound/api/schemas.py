from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    answer: str
    messages: list[str] | None = None
    complexity: str | None = None
    reasoning: str | None = None
    error: str | None = None

