from dependency_injector import containers, providers
from src.database import get_db_session
from src.repositories.sqlalchemy_client_repository import SqlAlchemyClientRepository
from src.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.services.client_service import ClientService
from src.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    """Container pour l'injection de dépendances."""

    # Database session factory
    db_session = providers.Factory(get_db_session)

    # Repositories - recréés à chaque appel avec une nouvelle session
    client_repository = providers.Factory(
        SqlAlchemyClientRepository,
        session=db_session,
    )

    user_repository = providers.Factory(
        SqlAlchemyUserRepository,
        session=db_session,
    )

    # Services
    client_service = providers.Factory(
        ClientService,
        repository=client_repository,
    )

    user_service = providers.Factory(
        UserService,
        repository=user_repository,
    )
