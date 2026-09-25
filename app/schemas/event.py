from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator

VALID_EVENT_TYPES = {"ORDERED", "SHIPPED", "DELAYED", "RECEIVED", "ANOMALY"}
VALID_STATUSES = {"PENDING", "PROCESSING", "PROCESSED", "FAILED"}


class SupplyEventCreate(BaseModel):
    supplier_id: str
    event_type: str
    payload: dict[str, Any] = {}
    idempotency_key: Optional[str] = None

    @field_validator("event_type")
    @classmethod
    def event_type_must_be_valid(cls, v: str) -> str:
        if v.upper() not in VALID_EVENT_TYPES:
            raise ValueError(f"event_type must be one of {VALID_EVENT_TYPES}")
        return v.upper()


class SupplyEventResponse(BaseModel):
    id: str
    supplier_id: str
    event_type: str
    payload: dict[str, Any]
    idempotency_key: Optional[str] = None
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SupplyEventFilter(BaseModel):
    supplier_id: Optional[str] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0
