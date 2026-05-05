from abc import ABC, abstractmethod

from src.domain.models.purchase import Purchase


class PurchaseRepository(ABC):

    @abstractmethod
    def execute_cypher(self, cypher: str) -> list[Purchase]:
        raise NotImplementedError("execute_cypher not implemented!")

    @abstractmethod
    def validate_cypher(self, cypher: str) -> bool:
        raise NotImplementedError("validate_cypher not implemented!")
