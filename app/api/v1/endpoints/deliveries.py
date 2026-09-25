from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models.delivery import WebhookDelivery
from app.schemas.delivery import WebhookDeliveryResponse

router = APIRouter()


@router.get("", response_model=list[WebhookDeliveryResponse])
def list_deliveries(
    event_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    query = db.query(WebhookDelivery)
    if event_id:
        query = query.filter(WebhookDelivery.event_id == event_id)
    if status:
        query = query.filter(WebhookDelivery.status == status.upper())
    return (
        query.order_by(WebhookDelivery.attempted_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post("/{delivery_id}/retry", response_model=WebhookDeliveryResponse)
def retry_delivery(
    delivery_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Manually trigger a retry for a failed webhook delivery."""
    delivery = db.query(WebhookDelivery).filter(
        WebhookDelivery.id == delivery_id
    ).first()

    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    if delivery.status == "SUCCESS":
        raise HTTPException(status_code=400, detail="Delivery already succeeded")

    from app.models.event import SupplyEvent
    from app.models.subscription import Subscription
    from app.services.webhook_service import _deliver_webhook

    event = db.query(SupplyEvent).filter(
        SupplyEvent.id == delivery.event_id
    ).first()
    sub = db.query(Subscription).filter(
        Subscription.id == delivery.subscription_id
    ).first()

    if not event or not sub:
        raise HTTPException(status_code=404, detail="Event or subscription not found")

    _deliver_webhook(db, event, sub, attempt_number=delivery.attempt_number + 1)
    db.refresh(delivery)
    return delivery
