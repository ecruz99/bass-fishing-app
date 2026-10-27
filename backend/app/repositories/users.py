from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import EmailAlreadyRegisteredError
from app.models import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """The user with this id, or None if there isn't one (for example, deleted)."""
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    """The user with this email, or None. Expects it already lowercased, as stored."""
    return db.scalar(select(User).where(User.email == email))


def create_user(db: Session, email: str, hashed_password: str) -> User:
    """Insert a user and return it with its database-generated fields loaded.

    Doesn't commit: the caller decides when the transaction ends. Raises
    EmailAlreadyRegisteredError if the email is taken.
    """
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    try:
        # Sends the INSERT now, so a duplicate fails here instead of at commit
        db.flush()
    except IntegrityError as error:
        # The unique index on email is the table's only constraint this insert can
        # break. Revisit if users gets another unique column.
        raise EmailAlreadyRegisteredError from error
    # Loads id, token_version and created_at, which the database filled in
    db.refresh(user)
    return user
