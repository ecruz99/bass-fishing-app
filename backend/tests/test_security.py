import jwt
import pytest

from app.config import settings
from app.security import (
    JWT_ALGORITHM,
    create_access_token,
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
