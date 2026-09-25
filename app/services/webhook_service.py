import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

import httpx

from app.config import settings
from app.db.session import SessionLocal
from app.models.delivery import WebhookDelivery
from app.models.event import SupplyEvent
from app.models.subscription import Subscription


def _sign_payload(secret_key: str, payload: str) -> str:
    """
    Sign a webhook payload with HMAC-SHA256.
    The receiver can verify the signature using the same secret.
    This proves the request came from Orisync, not a third party.
    """
    return hmac.new(
        secret_key.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()


def _matches_subscription(event: SupplyEvent, sub: Subscription) -> bool:
    """
    Check if an event should trigger a subscription.
    A subscription matches if:
    - It has no event_type filter (empty list = all types), OR
      the event type is in its filter list
    - It has no supplier filter (NULL = all suppliers), OR
      the event's supplier matches
    """
    type_match = (
        not sub.event_types or event.event_type in sub.event_types
    )
    supplier_match = (
        sub.supplier_id is None or sub.supplier_id == event.supplier_id
    )
    return type_match and supplier_match


def dispatch_webhooks(event_id: str) -> None:
    """
    Find all matching active subscriptions and deliver the event.
    Runs as a background task after event creation.
    Uses its own DB session since this runs outside the request context.
    """
    db = SessionLocal()
    try:
        event = db.query(SupplyEvent).filter(SupplyEvent.id == event_id).first()
        if not event:
            return

        # Mark event as processing
        event.status = "PROCESSING"
        db.commit()

        subscriptions = db.query(Subscription).filter(
            Subscription.is_active == True
        ).all()

        matching = [s for s in subscriptions if _matches_subscription(event, s)]

        if not matching:
            event.status = "PROCESSED"
            event.processed_at = datetime.now(timezone.utc)
            db.commit()
            return

        for sub in matching:
            _deliver_webhook(db, event, sub, attempt_number=1)

        event.status = "PROCESSED"
        event.processed_at = datetime.now(timezone.utc)
        db.commit()

    finally:
        db.close()


def _deliver_webhook(
    db,
    event: SupplyEvent,
    sub: Subscription,
    attempt_number: int,
) -> None:
    """
    Attempt to deliver one webhook. Logs every attempt.
    If delivery fails and retries remain, schedules next_retry_at.
    """
    payload_data = {
        "event_id": event.id,
        "event_type": event.event_type,
        "supplier_id": event.supplier_id,
        "payload": event.payload,
        "occurred_at": event.created_at.isoformat(),
    }
    payload_str = json.dumps(payload_data)

    headers = {"Content-Type": "application/json", "X-Orisync-Event": event.event_type}

    if sub.secret_key:
        signature = _sign_payload(sub.secret_key, payload_str)
        headers["X-Orisync-Signature"] = f"sha256={signature}"

    delivery = WebhookDelivery(
        event_id=event.id,
        subscription_id=sub.id,
        attempt_number=attempt_number,
        status="PENDING",
    )
    db.add(delivery)
    db.flush()

    try:
        with httpx.Client(timeout=settings.webhook_timeout_seconds) as client:
            response = client.post(
                sub.webhook_url,
                content=payload_str,
                headers=headers,
            )

        delivery.response_code = response.status_code
        delivery.response_body = response.text[:500]
        delivery.attempted_at = datetime.now(timezone.utc)

        if response.status_code < 400:
            delivery.status = "SUCCESS"
        else:
            delivery.status = "FAILED"
            _schedule_retry(delivery, attempt_number)

    except Exception as exc:
        delivery.status = "FAILED"
        delivery.response_body = str(exc)[:500]
        delivery.attempted_at = datetime.now(timezone.utc)
        _schedule_retry(delivery, attempt_number)

    db.commit()


def _schedule_retry(delivery: WebhookDelivery, attempt_number: int) -> None:
    """
    Set next_retry_at using exponential backoff if retries remain.
    Attempt 1 failed: retry in 60s
    Attempt 2 failed: retry in 120s
    Attempt 3 failed: retry in 240s
    After max retries: next_retry_at stays NULL (no more retries)
    """
    if attempt_number < settings.webhook_max_retries:
        delay = settings.webhook_retry_delay_seconds * (2 ** (attempt_number - 1))
        delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
