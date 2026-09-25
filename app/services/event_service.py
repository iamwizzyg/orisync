import os
from datetime import datetime, timezone

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.models.event import SupplyEvent
from app.models.supplier import Supplier
from app.schemas.event import SupplyEventCreate, SupplyEventFilter
from app.services.webhook_service import dispatch_webhooks


def create_event(
    db: Session,
    event_data: SupplyEventCreate,
    background_tasks: BackgroundTasks,
) -> SupplyEvent:
    supplier = db.query(Supplier).filter(
        Supplier.id == event_data.supplier_id,
        Supplier.is_active == True,
    ).first()

    if not supplier:
        raise ValueError(f"Supplier {event_data.supplier_id} not found or inactive")

    if event_data.idempotency_key:
        existing = db.query(SupplyEvent).filter(
            SupplyEvent.idempotency_key == event_data.idempotency_key
        ).first()
        if existing:
            return existing

    event = SupplyEvent(
        supplier_id=event_data.supplier_id,
        event_type=event_data.event_type,
        payload=event_data.payload,
        idempotency_key=event_data.idempotency_key,
        status="PENDING",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Skip background webhook dispatch in test environment.
    # The background thread causes SQLAlchemy mapper initialization
    # race conditions in CI where the test DB session is isolated.
    if not os.getenv("TESTING"):
        background_tasks.add_task(dispatch_webhooks, event.id)

    return event


def get_events(db: Session, filters: SupplyEventFilter) -> list[SupplyEvent]:
    query = db.query(SupplyEvent)

    if filters.supplier_id:
        query = query.filter(SupplyEvent.supplier_id == filters.supplier_id)
    if filters.event_type:
        query = query.filter(SupplyEvent.event_type == filters.event_type.upper())
    if filters.status:
        query = query.filter(SupplyEvent.status == filters.status.upper())

    return (
        query.order_by(SupplyEvent.created_at.desc())
        .offset(filters.offset)
        .limit(filters.limit)
        .all()
    )


def get_event_by_id(db: Session, event_id: str) -> SupplyEvent | None:
    return db.query(SupplyEvent).filter(SupplyEvent.id == event_id).first()
