from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import settings

# HMAC with SHA-256: the same secret signs and verifies. Fine while one service
# does both; an asymmetric algorithm only helps when others verify our tokens.
JWT_ALGORITHM = "HS256"


class InvalidTokenError(Exception):
    """The token can't be trusted: bad signature, expired, malformed or incomplete."""


@dataclass(frozen=True)
class TokenClaims:
    """What a verified access token says about its user."""

    user_id: int
    token_version: int


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


def decode_access_token(token: str) -> TokenClaims:
    """Verify a token from a request and return its claims.

    Raises InvalidTokenError for every kind of bad token, so callers handle one
    exception and the client never learns which check failed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            # Only our algorithm, never whatever the token's header claims.
            # This is what blocks "alg": "none" and algorithm-confusion attacks.
            algorithms=[JWT_ALGORITHM],
            # PyJWT checks exp automatically, but only if it's present
            options={"require": ["sub", "ver", "iat", "exp"]},
        )
    except jwt.InvalidTokenError as error:
        raise InvalidTokenError from error

    # The signature proves we issued it, so the claims have the shape we wrote
    return TokenClaims(user_id=int(payload["sub"]), token_version=payload["ver"])
