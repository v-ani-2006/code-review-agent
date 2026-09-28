import hashlib
import secrets
import bcrypt


def get_password_hash(password: str) -> str:
    """Generate a secure, salted bcrypt hash of a plaintext password using native bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash, with backward-compatibility for PBKDF2."""
    if not hashed_password or not plain_password:
        return False

    try:
        # 1. Standard bcrypt hash check ($2a$, $2b$, $2y$) using native bcrypt
        if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )

        # 2. Backward compatibility for Phase 3 PBKDF2 format (salt$hash)
        if "$" in hashed_password and not hashed_password.startswith("$"):
            salt, expected_hash = hashed_password.split("$", 1)
            computed_key = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                100_000,
            )
            return secrets.compare_digest(computed_key.hex(), expected_hash)

        return False
    except Exception:
        return False


# Alias to maintain full compatibility with Phase 3 repositories
hash_password = get_password_hash
