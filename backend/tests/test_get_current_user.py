from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import CurrentUser
from app.models import User
from app.security import create_access_token

# No real endpoint uses get_current_user yet, so test it through a minimal app
protected_app = FastAPI()


@protected_app.get("/whoami")
def whoami(user: CurrentUser) -> dict[str, int]:
    return {"id": user.id}


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    # Requests use the test's rolled-back session instead of a real one
    protected_app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(protected_app)
    protected_app.dependency_overrides.clear()


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(email="angler@example.com", hashed_password="hash")
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def assert_unauthorized(response: Response) -> None:
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_valid_token_returns_the_user(client: TestClient, user: User) -> None:
    token = create_access_token(user.id, user.token_version)

    response = client.get("/whoami", headers=auth_header(token))

    assert response.status_code == 200
    assert response.json() == {"id": user.id}


def test_missing_header_is_rejected(client: TestClient) -> None:
    assert_unauthorized(client.get("/whoami"))


def test_non_bearer_scheme_is_rejected(client: TestClient, user: User) -> None:
    token = create_access_token(user.id, user.token_version)

    response = client.get("/whoami", headers={"Authorization": f"Basic {token}"})

    assert_unauthorized(response)


def test_invalid_token_is_rejected(client: TestClient) -> None:
    assert_unauthorized(client.get("/whoami", headers=auth_header("not-a-jwt")))


def test_token_for_missing_user_is_rejected(client: TestClient) -> None:
    # A validly signed token whose user doesn't exist, for example after deletion
    token = create_access_token(user_id=999_999, token_version=0)

    assert_unauthorized(client.get("/whoami", headers=auth_header(token)))


def test_token_with_old_version_is_rejected(
    client: TestClient, user: User, db_session: Session
) -> None:
    token = create_access_token(user.id, user.token_version)
    # What change password and log out everywhere will do
    user.token_version += 1
    db_session.flush()

    assert_unauthorized(client.get("/whoami", headers=auth_header(token)))
