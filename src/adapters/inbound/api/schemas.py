from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    answer: str
    path: str
    preferred_path: str
    messages: list[str] | None = None
