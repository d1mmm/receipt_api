import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

@pytest.fixture(scope="session", autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def register_user(client):
    def _register(username: str = "user", full_name: str = "User", password: str = "pass"):
        return client.post(
            "/register",
            json={"username": username, "full_name": full_name, "password": password}
        )
    return _register

@pytest.fixture
def login_user(client, register_user):
    def _login(username: str = "user", password: str = "pass"):
        # ensure user exists
        register_user(username, "User", password)
        return client.post(
            "/login",
            json={"username": username, "password": password}
        )
    return _login
