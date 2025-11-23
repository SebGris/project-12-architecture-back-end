"""Event model for Epic Events CRM."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from .contract import Contract
    from .user import User


class Event(Base):
    """Event model representing events organized by Epic Events."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    event_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    event_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    attendees: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Foreign keys
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id"), nullable=False
    )
    support_contact_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    # Relationships
    contract: Mapped["Contract"] = relationship(
        "Contract", back_populates="events", lazy="select"
    )
    support_contact: Mapped[Optional["User"]] = relationship(
        "User", back_populates="support_events", lazy="select"
    )

    # Check constraints
    __table_args__ = (
        CheckConstraint(
            "event_end > event_start", name="check_event_dates_valid"
        ),
        CheckConstraint("attendees >= 0", name="check_attendees_positive"),
    )

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, name='{self.name}', contract_id={self.contract_id})>"
