import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    event_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("supply_events.id"),
        nullable=False,
        index=True,
    )
    subscription_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("subscriptions.id"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING")
    # PENDING → SUCCESS or FAILED

    response_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # HTTP status code returned by the webhook endpoint.
    # NULL if the request never completed (timeout, DNS failure).

    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # When the next retry attempt should be made.
    # NULL means no retry scheduled (success or max retries reached).

    # Relationships
    event: Mapped["SupplyEvent"] = relationship(  # type: ignore
        "SupplyEvent", back_populates="deliveries"
    )
    subscription: Mapped["Subscription"] = relationship(  # type: ignore
        "Subscription", back_populates="deliveries"
    )

    def __repr__(self) -> str:
        return f"<WebhookDelivery attempt={self.attempt_number} status={self.status}>"
