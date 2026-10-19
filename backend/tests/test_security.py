from app.security import hash_password, verify_password


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
