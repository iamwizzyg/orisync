import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    webhook_url: Mapped[str] = mapped_column(String, nullable=False)
    event_types: Mapped[list] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )
    # Which event types trigger this subscription.
    # Empty list means all event types.
    # Example: ["DELAYED", "ANOMALY"]

    supplier_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("suppliers.id"),
        nullable=True,
        index=True,
    )
    # NULL means: watch events from ALL suppliers.
    # A specific supplier_id means: watch only that supplier.

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    secret_key: Mapped[str | None] = mapped_column(String, nullable=True)
    # Used to sign webhook payloads with HMAC-SHA256.
    # The receiver verifies the signature to confirm the
    # request genuinely came from Orisync.

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    supplier: Mapped["Supplier"] = relationship(  # type: ignore
        "Supplier", back_populates="subscriptions"
    )
    deliveries: Mapped[list] = relationship(
        "WebhookDelivery", back_populates="subscription"
    )

    def __repr__(self) -> str:
        return f"<Subscription url={self.webhook_url}>"
