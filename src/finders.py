import sqlite3
from typing import Callable, List

from src.models.client import Client


class DbFinder:

    def __init__(self, client_factory: Callable[..., Client]) -> None:
        self._client_factory = client_factory

    def find_all(self) -> List[Client]:
        raise NotImplementedError()


class SqliteClientFinder(DbFinder):

    def __init__(
        self,
        client_factory: Callable[..., Client],
        path: str,
    ) -> None:
        self._database = sqlite3.connect(path)
        super().__init__(client_factory)

    def find_all(self) -> List[Client]:
        with self._database as db:
            rows = db.execute("SELECT * FROM clients")
            return [self._client_factory(*row) for row in rows]
