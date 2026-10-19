from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import settings

# HMAC with SHA-256: the same secret signs and verifies. Fine while one service
# does both; an asymmetric algorithm only helps when others verify our tokens.
JWT_ALGORITHM = "HS256"

# Argon2id with pwdlib's recommended settings. The algorithm, settings and salt
# are stored inside each hash string, so verify() needs nothing else.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password for storage. Each call uses a new random salt."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Check a password against a stored hash.

    A malformed hash raises pwdlib's UnknownHashError instead of returning False,
    since that's a bug in our data, not a wrong password.
    """
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int, token_version: int) -> str:
    """Create a signed JWT that identifies the user until it expires.

    `ver` is the user's token_version at login. get_current_user rejects the token
    once the stored version moves past it (password change, log out everywhere).
    """
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),  # the JWT spec requires a string subject
        "ver": token_version,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
