"""
Implementación de IPasswordHasher usando Django's contrib.auth.hashers.
"""
from django.contrib.auth.hashers import make_password, check_password

from domain.interfaces.i_password_hasher import IPasswordHasher


class DjangoPasswordHasher(IPasswordHasher):
    """Implementación de hash usando Django."""

    def hash_password(self, password: str) -> str:
        return make_password(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return check_password(plain_password, hashed_password)
