"""Password hashing with Argon2."""

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()

# Verified against when the user does not exist, so a missing account takes
# as long to reject as a wrong password.
_DUMMY_HASH = _password_hash.hash("dummy-password")


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return _password_hash.hash(password)


def verify_password(password: str, hashed_password: str | None) -> bool:
    """Check a password against a stored hash.

    Args:
        password: Plain password from the request.
        hashed_password: Stored hash, or None if the user was not found.

    Returns:
        True if the password matches.
    """
    if hashed_password is None:
        _password_hash.verify(password, _DUMMY_HASH)
        return False
    return _password_hash.verify(password, hashed_password)
