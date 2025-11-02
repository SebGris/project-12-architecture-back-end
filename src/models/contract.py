"""Contract model for Epic Events CRM."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from .client import Client
    from .event import Event


class Contract(Base):
    """Contract model representing contracts between clients and Epic Events."""

    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    is_signed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Foreign key to Client
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"), nullable=False
    )

    # Relationships
    client: Mapped["Client"] = relationship(
        "Client", back_populates="contracts", lazy="select"
    )
    events: Mapped[List["Event"]] = relationship(
        "Event", back_populates="contract", lazy="select"
    )

    # Check constraints
    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0", name="check_total_amount_positive"
        ),
        CheckConstraint(
            "remaining_amount >= 0", name="check_remaining_amount_positive"
        ),
        CheckConstraint(
            "remaining_amount <= total_amount",
            name="check_remaining_lte_total",
        ),
    )

    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, client_id={self.client_id}, signed={self.is_signed})>"
