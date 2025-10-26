from dependency_injector import containers, providers

from .database import Database
from src.repositories.client_repository import ClientRepository
from src.services.client_service import ClientService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])

    config = providers.Configuration()
    config.database_url.from_env("DATABASE_URL")
    config.secret_key.from_env("SECRET_KEY", required=True)

    db = providers.Singleton(Database, db_url=config.database_url)

    client_repository = providers.Factory(
        ClientRepository,
        session_factory=db.provided.session,
    )

    client_service = providers.Factory(
        ClientService,
        client_repository=client_repository,
    )
