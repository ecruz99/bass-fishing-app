import pytest
from sqlalchemy.orm import Session

from app.exceptions import EmailAlreadyRegisteredError
from app.repositories.users import create_user


def test_create_user_returns_saved_user(db_session: Session) -> None:
    user = create_user(db_session, "angler@example.com", "hash")

    assert user.id is not None
    assert user.email == "angler@example.com"
    assert user.hashed_password == "hash"
    assert user.token_version == 0
    assert user.created_at is not None


def test_create_user_with_taken_email_raises(db_session: Session) -> None:
    create_user(db_session, "angler@example.com", "hash")

    with pytest.raises(EmailAlreadyRegisteredError):
        create_user(db_session, "angler@example.com", "other")
