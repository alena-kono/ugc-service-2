from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(secret=password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(secret=password, hash=hashed_password)
