"""Client model for Epic Events CRM."""

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base


class Client(Base):
    """Client model representing customers of Epic Events."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Foreign key to User (sales contact - Commercial)
    sales_contact_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships (to be fully implemented with back_populates)
    # sales_contact: Mapped["User"] = relationship("User", back_populates="clients")
    # contracts: Mapped[list["Contract"]] = relationship("Contract", back_populates="client")

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.first_name} {self.last_name}', company='{self.company_name}')>"
