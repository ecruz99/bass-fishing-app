import pytest
from sqlalchemy.orm import Session

from app.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.security import decode_access_token, verify_password
from app.services import auth
from app.services.auth import log_in, register_user


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


def test_log_in_returns_token_for_the_user(db_session: Session) -> None:
    user = register_user(db_session, "angler@example.com", "correct horse")

    claims = decode_access_token(
        log_in(db_session, "Angler@Example.com", "correct horse")
    )

    assert claims.user_id == user.id
    assert claims.token_version == user.token_version


def test_log_in_rejects_wrong_password(db_session: Session) -> None:
    register_user(db_session, "angler@example.com", "correct horse")

    with pytest.raises(InvalidCredentialsError):
        log_in(db_session, "angler@example.com", "wrong password")


def test_log_in_rejects_unknown_email(db_session: Session) -> None:
    with pytest.raises(InvalidCredentialsError):
        log_in(db_session, "nobody@example.com", "correct horse")


def test_log_in_hashes_even_for_unknown_email(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Measuring time would be flaky, so check the expensive call still happens
    calls: list[str] = []

    def spy(password: str, hashed_password: str) -> bool:
        calls.append(hashed_password)
        return verify_password(password, hashed_password)

    monkeypatch.setattr(auth, "verify_password", spy)

    with pytest.raises(InvalidCredentialsError):
        log_in(db_session, "nobody@example.com", "correct horse")

    assert calls == [auth.DUMMY_HASH]
