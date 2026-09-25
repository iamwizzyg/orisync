# This file exists solely for Alembic to discover all models.
# Import it in alembic/env.py instead of app.db.base
from app.db.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.supplier import Supplier  # noqa: F401
from app.models.event import SupplyEvent  # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.models.delivery import WebhookDelivery  # noqa: F401
