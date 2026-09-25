from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class SupplierCreate(BaseModel):
    name: str
    contact_email: Optional[EmailStr] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseModel):
    id: str
    name: str
    contact_email: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
