from sqlalchemy.orm import Session

from app.models import User
from app.repositories.users import create_user
from app.security import hash_password


def register_user(db: Session, email: str, password: str) -> User:
    """Create an account and commit it. Expects an already validated email and password.

    Raises EmailAlreadyRegisteredError if the email is taken, in any letter case.
    """
    # Lowercased before every insert and lookup, so the unique index on email
    # also blocks "Angler@x.com" when "angler@x.com" exists
    user = create_user(db, email.lower(), hash_password(password))
    db.commit()
    return user
