from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.security import decode_access_token

SIGNUP_URL = "/api/v1/auth/signup"
LOGIN_URL = "/api/v1/auth/login"
CREDENTIALS = {"email": "angler@example.com", "password": "correct horse"}


@pytest.fixture
def user_id(client: TestClient) -> int:
    """Signs up the account in CREDENTIALS and returns its id."""
    response = client.post(SIGNUP_URL, json=CREDENTIALS)
    user_id: int = response.json()["id"]
    return user_id


def test_login_returns_token_for_the_user(client: TestClient, user_id: int) -> None:
    response = client.post(LOGIN_URL, json=CREDENTIALS)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert decode_access_token(body["access_token"]).user_id == user_id


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "angler@example.com", "password": "wrong password"},
        {"email": "nobody@example.com", "password": "correct horse"},
    ],
)
@pytest.mark.usefixtures("user_id")
def test_login_failures_look_the_same(
    client: TestClient, payload: dict[str, str]
) -> None:
    response = client.post(LOGIN_URL, json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "correct horse"},
        {"email": "angler@example.com", "password": "x" * 129},
        {"email": "angler@example.com"},
        {},
    ],
)
def test_login_with_invalid_body_returns_422(
    client: TestClient, payload: dict[str, Any]
) -> None:
    assert client.post(LOGIN_URL, json=payload).status_code == 422
