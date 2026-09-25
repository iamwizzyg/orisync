from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "VIEWER"

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        valid_roles = {"ADMIN", "OPERATOR", "VIEWER"}
        if v.upper() not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")
        return v.upper()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
    # from_attributes=True tells Pydantic to read values
    # from SQLAlchemy model attributes, not just dicts.
    # Without this, converting a DB model to a schema fails.


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
