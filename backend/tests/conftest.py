import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app
from app.routers import posts as posts_router


@pytest.fixture(name="session")
def session_fixture():
    # SQLite en memoria: cada test arranca con una base limpia y rápida
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session, tmp_path, monkeypatch):
    monkeypatch.setattr(posts_router, "UPLOADS_DIR", str(tmp_path))

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(name="login")
def login_fixture(client):
    """Devuelve una función que registra un usuario y retorna sus headers."""

    def _login(username="ana", password="secreta1"):
        client.post(
            "/auth/register",
            json={
                "username": username,
                "email": f"{username}@test.com",
                "password": password,
            },
        )
        res = client.post(
            "/auth/token", data={"username": username, "password": password}
        )
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    return _login
