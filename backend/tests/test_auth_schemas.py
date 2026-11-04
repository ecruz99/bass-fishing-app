import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.auth import LoginRequest, SignupRequest, UserResponse


def test_signup_request_accepts_valid_input() -> None:
    request = SignupRequest(email="angler@example.com", password="correct horse")

    assert request.email == "angler@example.com"
    assert request.password == "correct horse"


@pytest.mark.parametrize("email", ["not-an-email", "angler@", "@example.com", ""])
def test_signup_request_rejects_invalid_email(email: str) -> None:
    with pytest.raises(ValidationError):
        SignupRequest(email=email, password="correct horse")


@pytest.mark.parametrize("length", [8, 128])
def test_signup_request_accepts_password_length_limits(length: int) -> None:
    request = SignupRequest(email="angler@example.com", password="x" * length)

    assert len(request.password) == length


@pytest.mark.parametrize("length", [0, 7, 129])
def test_signup_request_rejects_password_outside_limits(length: int) -> None:
    with pytest.raises(ValidationError):
        SignupRequest(email="angler@example.com", password="x" * length)


@pytest.mark.parametrize("length", [0, 1, 128])
def test_login_request_accepts_any_password_up_to_the_cap(length: int) -> None:
    request = LoginRequest(email="angler@example.com", password="x" * length)

    assert len(request.password) == length


def test_login_request_rejects_password_over_the_cap() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="angler@example.com", password="x" * 129)


def test_user_response_leaves_out_private_fields(db_session: Session) -> None:
    user = User(email="angler@example.com", hashed_password="hash")
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)

    response = UserResponse.model_validate(user)

    assert response.model_dump().keys() == {"id", "email", "created_at"}
