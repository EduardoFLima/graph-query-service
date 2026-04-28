from typing import Optional

from fastapi import APIRouter, Cookie, Response

from src.adapters.inbound.api.schemas import (
    ChatRequest,
    ChatResponse,
)
from src.dependencies import ChatServiceDep

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, response_model_exclude_none=True)
def receive_question(request: ChatRequest,
                     response: Response,
                     service: ChatServiceDep,
                     user_id: Optional[str] = None,
                     show_history: Optional[bool] = None,
                     thread_id: str = Cookie(None)):
    chat_response = service.chat(thread_id, request.prompt, user_id)

    response.set_cookie("thread_id", chat_response.get("thread_id"))

    if chat_response["blocked"]:
        response.status_code = 400

    return ChatResponse(
        messages=chat_response.get("messages") if show_history else None,
        answer=chat_response.get("answer"),
        path=str(chat_response.get("path")),
        preferred_path=str(chat_response.get("preferred_path"))
    )
