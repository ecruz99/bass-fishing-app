from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.error_handlers import register_error_handlers

# A minimal app with the handlers installed, so these tests don't depend on
# any real endpoint
error_app = FastAPI()
register_error_handlers(error_app)


class Credentials(BaseModel):
    password: str = Field(min_length=8)


@error_app.post("/echo")
def echo(body: Credentials) -> dict[str, str]:
    return {"status": "ok"}


@error_app.get("/bug")
def bug() -> None:
    raise RuntimeError("database password is hunter2")


# Without raise_server_exceptions=False, TestClient re-raises the bug in the test
client = TestClient(error_app, raise_server_exceptions=False)


def test_validation_error_lists_fields_without_echoing_input() -> None:
    response = client.post("/echo", json={"password": "secret1"})

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Invalid request",
        "errors": [
            {
                "field": "body.password",
                "message": "String should have at least 8 characters",
            }
        ],
    }
    assert "secret1" not in response.text


def test_malformed_json_gets_the_same_shape() -> None:
    response = client.post(
        "/echo", content="not json", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid request"
    assert "not json" not in response.text


def test_unexpected_error_returns_json_without_its_message() -> None:
    response = client.get("/bug")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "hunter2" not in response.text
