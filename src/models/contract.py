"""Contract model for Epic Events CRM."""

from datetime import datetime
from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base


class Contract(Base):
    """Contract model representing contracts between clients and Epic Events."""

    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    remaining_amount: Mapped[float] = mapped_column(
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

    # Relationships (to be fully implemented)
    # client: Mapped["Client"] = relationship("Client", back_populates="contracts")
    # events: Mapped[list["Event"]] = relationship("Event", back_populates="contract")

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
