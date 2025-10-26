from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.client import Client


class ClientRepository(ABC):

    @abstractmethod
    def get_by_id(self, client_id: str) -> Optional[Client]:
        pass

    @abstractmethod
    def add(self, client: Client) -> None:
        pass

    @abstractmethod
    def list_all(self) -> List[Client]:
        pass
