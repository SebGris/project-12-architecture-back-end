"""User model for Epic Events CRM.

This module contains the User model representing employees.
Password hashing logic is in UserService (SRP compliance).
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Enum as SQLEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from .client import Client
    from .event import Event


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
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
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

    # Relationships
    clients: Mapped[List["Client"]] = relationship(
        "Client", back_populates="sales_contact", lazy="select"
    )
    support_events: Mapped[List["Event"]] = relationship(
        "Event", back_populates="support_contact", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', department={self.department})>"
