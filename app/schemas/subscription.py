from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class SubscriptionCreate(BaseModel):
    name: Optional[str] = None
    webhook_url: str
    event_types: list[str] = []
    supplier_id: Optional[str] = None
    secret_key: Optional[str] = None

    @field_validator("event_types")
    @classmethod
    def validate_event_types(cls, v: list[str]) -> list[str]:
        valid = {"ORDERED", "SHIPPED", "DELAYED", "RECEIVED", "ANOMALY"}
        for event_type in v:
            if event_type.upper() not in valid:
                raise ValueError(f"{event_type} is not a valid event type")
        return [e.upper() for e in v]

    @field_validator("webhook_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("webhook_url must start with http:// or https://")
        return v


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    event_types: Optional[list[str]] = None
    is_active: Optional[bool] = None


class SubscriptionResponse(BaseModel):
    id: str
    name: Optional[str] = None
    webhook_url: str
    event_types: list[str]
    supplier_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
