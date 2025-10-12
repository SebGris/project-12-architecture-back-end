from enum import Enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column
from . import Base


class Department(str, Enum):
    """User department enumeration."""

    COMMERCIAL = "COMMERCIAL"
    GESTION = "GESTION"
    SUPPORT = "SUPPORT"


class User(Base):
    """User model representing employees of Epic Events."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    department: Mapped[Department] = mapped_column(
        SQLEnum(Department), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def set_password(self, password: str) -> None:
        """Hash and set password (to be implemented with bcrypt)."""
        # TODO: Implement with passlib bcrypt
        raise NotImplementedError("Password hashing not implemented yet")

    def verify_password(self, password: str) -> bool:
        """Verify password against hash (to be implemented with bcrypt)."""
        # TODO: Implement with passlib bcrypt
        raise NotImplementedError("Password verification not implemented yet")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', department={self.department})>"
