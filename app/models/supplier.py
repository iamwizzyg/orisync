import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship: one supplier has many supply events
    events: Mapped[list] = relationship("SupplyEvent", back_populates="supplier")

    # Relationship: one supplier can have many subscriptions watching it
    subscriptions: Mapped[list] = relationship(
        "Subscription", back_populates="supplier"
    )

    def __repr__(self) -> str:
        return f"<Supplier name={self.name}>"
