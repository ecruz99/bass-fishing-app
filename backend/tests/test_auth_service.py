import pytest
from sqlalchemy.orm import Session

from app.exceptions import EmailAlreadyRegisteredError
from app.security import verify_password
from app.services.auth import register_user


def test_register_user_stores_lowercased_email(db_session: Session) -> None:
    user = register_user(db_session, "Angler@Example.COM", "correct horse")

    assert user.email == "angler@example.com"


def test_register_user_stores_a_hash_not_the_password(db_session: Session) -> None:
    user = register_user(db_session, "angler@example.com", "correct horse")

    assert user.hashed_password != "correct horse"
    assert verify_password("correct horse", user.hashed_password)


def test_register_user_rejects_email_taken_in_another_case(
    db_session: Session,
) -> None:
    register_user(db_session, "angler@example.com", "correct horse")

    with pytest.raises(EmailAlreadyRegisteredError):
        register_user(db_session, "ANGLER@example.com", "another password")
