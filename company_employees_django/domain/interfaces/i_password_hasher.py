"""
Interfaz para el servicio de Hashing de contraseñas.
"""
from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Contrato para hashing de contraseñas."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Genera el hash seguro de una contraseña."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña en texto plano coincide con su hash."""
        pass
