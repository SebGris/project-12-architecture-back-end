from enum import Enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column
import bcrypt
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
        """Hash and set password using bcrypt."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """Verify password against hash using bcrypt."""
        password_bytes = password.encode("utf-8")
        hash_bytes = self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', department={self.department})>"
