from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import pytest

from app.config import settings
from app.security import (
    JWT_ALGORITHM,
    InvalidTokenError,
    TokenClaims,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_argon2id_and_not_the_password() -> None:
    hashed = hash_password("correct horse")

    assert hashed.startswith("$argon2id$")
    assert "correct horse" not in hashed


def test_correct_password_verifies() -> None:
    hashed = hash_password("correct horse")

    assert verify_password("correct horse", hashed)


def test_wrong_password_does_not_verify() -> None:
    hashed = hash_password("correct horse")

    assert not verify_password("Correct horse", hashed)


def test_same_password_hashes_differently() -> None:
    # A random salt per hash means equal passwords don't produce equal hashes,
    # so a leaked table doesn't show which users share a password
    assert hash_password("correct horse") != hash_password("correct horse")


def test_access_token_carries_user_and_version() -> None:
    token = create_access_token(user_id=42, token_version=3)

    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])

    assert payload["sub"] == "42"
    assert payload["ver"] == 3


def test_access_token_expires_after_configured_minutes() -> None:
    token = create_access_token(user_id=42, token_version=0)

    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])

    lifetime = payload["exp"] - payload["iat"]
    assert lifetime == settings.access_token_expire_minutes * 60


def test_access_token_is_signed_with_the_secret() -> None:
    token = create_access_token(user_id=42, token_version=0)

    # Only someone with our secret can produce a token that passes verification
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(
            token,
            "a-different-secret-that-is-at-least-32-bytes",
            algorithms=[JWT_ALGORITHM],
        )


def make_token(
    claims: dict[str, Any], key: str | None = None, algorithm: str = JWT_ALGORITHM
) -> str:
    """Build a token by hand, for the cases create_access_token never produces."""
    return jwt.encode(claims, key or settings.jwt_secret_key, algorithm=algorithm)


def valid_claims() -> dict[str, Any]:
    now = datetime.now(UTC)
    return {"sub": "42", "ver": 3, "iat": now, "exp": now + timedelta(minutes=5)}


def test_decode_returns_claims_from_a_valid_token() -> None:
    token = create_access_token(user_id=42, token_version=3)

    assert decode_access_token(token) == TokenClaims(user_id=42, token_version=3)


def test_decode_rejects_expired_token() -> None:
    claims = valid_claims() | {"exp": datetime.now(UTC) - timedelta(seconds=1)}

    with pytest.raises(InvalidTokenError):
        decode_access_token(make_token(claims))


def test_decode_rejects_token_signed_with_another_secret() -> None:
    token = make_token(valid_claims(), key="an-attackers-secret-that-is-32-bytes-long")

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_rejects_tampered_payload() -> None:
    header, _, signature = create_access_token(user_id=42, token_version=3).split(".")
    # Swap in a payload claiming to be user 1, keeping the original signature
    forged_payload = make_token(valid_claims() | {"sub": "1"}).split(".")[1]

    with pytest.raises(InvalidTokenError):
        decode_access_token(f"{header}.{forged_payload}.{signature}")


def test_decode_rejects_unsigned_alg_none_token() -> None:
    token = jwt.encode(valid_claims(), key=None, algorithm="none")

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


@pytest.mark.parametrize("claim", ["sub", "ver", "iat", "exp"])
def test_decode_rejects_token_missing_a_claim(claim: str) -> None:
    claims = valid_claims()
    del claims[claim]

    with pytest.raises(InvalidTokenError):
        decode_access_token(make_token(claims))


def test_decode_rejects_garbage() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("not-a-jwt")
