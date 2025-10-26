from typing import List, Optional
from sqlalchemy.orm import Session
from src.repositories.client_repository import ClientRepository
from src.models.client import Client


class SqlAlchemyClientRepository(ClientRepository):

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, client_id: str) -> Optional[Client]:
        return self.session.query(Client).filter_by(id=client_id).first()

    def add(self, client: Client) -> None:
        self.session.add(client)
        self.session.commit()

    def list_all(self) -> List[Client]:
        return self.session.query(Client).all()
