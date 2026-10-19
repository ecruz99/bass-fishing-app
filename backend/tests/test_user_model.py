import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User


def test_new_user_gets_database_defaults(db_session: Session) -> None:
    user = User(email="angler@example.com", hashed_password="hash")
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)

    assert user.id is not None
    assert user.token_version == 0
    assert user.created_at is not None
    assert user.created_at.tzinfo is not None


def test_email_must_be_unique(db_session: Session) -> None:
    db_session.add(User(email="angler@example.com", hashed_password="hash"))
    db_session.flush()

    # The database enforces this, so two signups racing each other can't both win
    db_session.add(User(email="angler@example.com", hashed_password="other"))
    with pytest.raises(IntegrityError):
        db_session.flush()
