from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    deliveries,
    events,
    subscriptions,
    suppliers,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["Deliveries"])
