import pytest
from sqlalchemy.orm import Session

from app.exceptions import EmailAlreadyRegisteredError
from app.repositories.users import create_user, get_user_by_email


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


def test_get_user_by_email_finds_user(db_session: Session) -> None:
    created = create_user(db_session, "angler@example.com", "hash")

    assert get_user_by_email(db_session, "angler@example.com") == created


def test_get_user_by_email_returns_none_for_unknown_email(db_session: Session) -> None:
    assert get_user_by_email(db_session, "nobody@example.com") is None
