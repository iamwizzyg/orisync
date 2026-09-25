import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SupplyEvent(Base):
    __tablename__ = "supply_events"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    supplier_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Valid values: ORDERED, SHIPPED, DELAYED, RECEIVED, ANOMALY

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Flexible JSON storage for event-specific data.
    # JSONB is stored as binary in PostgreSQL, making it
    # queryable and indexable unlike plain JSON strings.

    idempotency_key: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    # Unique constraint prevents the same event being stored twice.
    # Callers include this key; duplicate submissions are rejected.

    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING")
    # State machine: PENDING → PROCESSING → PROCESSED or FAILED

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    supplier: Mapped["Supplier"] = relationship(  # type: ignore
        "Supplier", back_populates="events"
    )
    deliveries: Mapped[list] = relationship(
        "WebhookDelivery", back_populates="event"
    )

    def __repr__(self) -> str:
        return f"<SupplyEvent type={self.event_type} status={self.status}>"
