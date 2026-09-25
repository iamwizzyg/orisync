from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Every model in app/models/ inherits from this.
    """
    pass


# Import all models here so Alembic can detect them
# when generating migrations. Order matters if there
# are foreign key dependencies.
from app.models.user import User  # noqa: F401, E402
from app.models.supplier import Supplier  # noqa: F401, E402
from app.models.event import SupplyEvent  # noqa: F401, E402
from app.models.subscription import Subscription  # noqa: F401, E402
from app.models.delivery import WebhookDelivery  # noqa: F401, E402
