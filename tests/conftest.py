import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.base_all import *  # noqa: F401, F403
from app.db.session import get_db
from app.main import app
from app.models.user import User

TEST_DATABASE_URL = settings.database_url.replace(
    "/orisync_db", "/orisync_test"
)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def create_test_database():
    admin_url = settings.database_url.replace("/orisync_db", "/postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname='orisync_test'")
        )
        if not result.fetchone():
            conn.execute(text("CREATE DATABASE orisync_test"))
    admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    create_test_database()
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    yield session
    session.close()
    # Clean all tables respecting FK constraints
    with test_engine.begin() as conn:
        conn.execute(text("SET session_replication_role = replica"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("SET session_replication_role = DEFAULT"))


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _create_user_and_token(db, email: str, password: str, role: str) -> str:
    """
    Directly create a user in the DB and return a valid JWT.
    Bypasses the HTTP layer to avoid session visibility issues.
    """
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return create_access_token(data={"sub": user.email})


@pytest.fixture()
def admin_token(db):
    return _create_user_and_token(db, "admin@orisync.test", "adminpass123", "ADMIN")


@pytest.fixture()
def operator_token(db):
    return _create_user_and_token(db, "operator@orisync.test", "operatorpass123", "OPERATOR")


@pytest.fixture()
def viewer_token(db):
    return _create_user_and_token(db, "viewer@orisync.test", "viewerpass123", "VIEWER")


@pytest.fixture()
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def operator_headers(operator_token):
    return {"Authorization": f"Bearer {operator_token}"}


@pytest.fixture()
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture()
def sample_supplier(db, auth_headers, client):
    response = client.post(
        "/api/v1/suppliers",
        json={"name": "Test Supplier Ltd", "contact_email": "supplier@test.com"},
        headers=auth_headers,
    )
    return response.json()
