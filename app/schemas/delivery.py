from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WebhookDeliveryResponse(BaseModel):
    id: str
    event_id: str
    subscription_id: str
    attempt_number: int
    status: str
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    attempted_at: datetime
    next_retry_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
