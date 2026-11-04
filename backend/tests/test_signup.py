from typing import Any

import pytest
from fastapi.testclient import TestClient

SIGNUP_URL = "/api/v1/auth/signup"


def test_signup_creates_user(client: TestClient) -> None:
    response = client.post(
        SIGNUP_URL, json={"email": "Angler@Example.com", "password": "correct horse"}
    )

    assert response.status_code == 201
    body = response.json()
    # Exactly these fields: no password hash or token version
    assert body.keys() == {"id", "email", "created_at"}
    assert body["email"] == "angler@example.com"


def test_signup_with_taken_email_returns_409(client: TestClient) -> None:
    client.post(
        SIGNUP_URL, json={"email": "angler@example.com", "password": "correct horse"}
    )

    response = client.post(
        SIGNUP_URL, json={"email": "ANGLER@example.com", "password": "other password"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "correct horse"},
        {"email": "angler@example.com", "password": "short"},
        {"email": "angler@example.com"},
        {},
    ],
)
def test_signup_with_invalid_body_returns_422(
    client: TestClient, payload: dict[str, Any]
) -> None:
    assert client.post(SIGNUP_URL, json=payload).status_code == 422
