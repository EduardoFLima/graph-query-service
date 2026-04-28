from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")

class ModelClientPort(ABC):

    @abstractmethod
    def send_prompt(self, system_prompt: str, user_prompt: str, response_format: type[T]) -> T:
        raise NotImplementedError("send_prompt is not implemented")

    @abstractmethod
    def safeguard_check(self, safeguard_prompt: str, response_format: type[T]) -> T:
        raise NotImplementedError("safeguard_check is not implemented")