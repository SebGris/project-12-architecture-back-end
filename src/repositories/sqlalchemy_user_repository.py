from sqlalchemy.orm import Session
from src.repositories.user_repository import UserRepository
from src.models.user import User


class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, user: User) -> User:
        """Add a new user to the database.

        Args:
            user: User instance to add

        Returns:
            The added User instance (with ID populated after commit)
        """
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get(self, user_id: int) -> User:
        """Get a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User instance or None if not found
        """
        return self.session.query(User).filter_by(id=user_id).first()

    def get_by_username(self, username: str) -> User:
        """Get a user by username.

        Args:
            username: The user's username

        Returns:
            User instance or None if not found
        """
        return self.session.query(User).filter_by(username=username).first()

    def get_by_email(self, email: str) -> User:
        """Get a user by email.

        Args:
            email: The user's email

        Returns:
            User instance or None if not found
        """
        return self.session.query(User).filter_by(email=email).first()
