from abc import ABC, abstractmethod
from typing import Final

NOT_IMPLEMENTED_ERROR_MSG: Final = "Method not implemented"

class ChatUseCase(ABC):

    @abstractmethod
    def chat(self, thread_id: str, prompt: str, user_id: str) -> dict:
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR_MSG)
