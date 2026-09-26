from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# The engine is the actual connection to PostgreSQL.
# pool_pre_ping=True means SQLAlchemy tests the connection
# before using it, automatically reconnecting if it dropped.
engine = create_engine(
    settings.sqlalchemy_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# SessionLocal is a factory that creates database sessions.
# autocommit=False means changes are not saved until you
# explicitly call session.commit().
# autoflush=False means SQLAlchemy waits for you to flush
# rather than doing it automatically before every query.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    FastAPI dependency that provides a database session.
    Opens a session, yields it to the route handler,
    then closes it when the request is finished.
    The try/finally ensures the session closes even if
    an exception occurs during the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
