from pwdlib import PasswordHash

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
