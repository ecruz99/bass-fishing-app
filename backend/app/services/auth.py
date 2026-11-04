from sqlalchemy.orm import Session

from app.exceptions import InvalidCredentialsError
from app.models import User
from app.repositories.users import create_user, get_user_by_email
from app.security import create_access_token, hash_password, verify_password

# Hashed once, when the module loads. An unknown email is checked against it so that
# path does the same Argon2 work as a wrong password, and response time doesn't
# reveal which emails have accounts.
DUMMY_HASH = hash_password("dummy password, never matches a real login")


def register_user(db: Session, email: str, password: str) -> User:
    """Create an account and commit it. Expects an already validated email and password.

    Raises EmailAlreadyRegisteredError if the email is taken, in any letter case.
    """
    # Lowercased before every insert and lookup, so the unique index on email
    # also blocks "Angler@x.com" when "angler@x.com" exists
    user = create_user(db, email.lower(), hash_password(password))
    db.commit()
    return user


def log_in(db: Session, email: str, password: str) -> str:
    """Check an email and password and return a new access token for that user.

    Raises InvalidCredentialsError for an unknown email or a wrong password alike.
    """
    user = get_user_by_email(db, email.lower())
    if user is None:
        verify_password(password, DUMMY_HASH)
        raise InvalidCredentialsError
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError
    return create_access_token(user.id, user.token_version)
