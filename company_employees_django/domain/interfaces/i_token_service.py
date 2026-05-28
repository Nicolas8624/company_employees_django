"""
Interfaz para el servicio generador de Tokens.
"""
from abc import ABC, abstractmethod

from domain.entities.usuario import Usuario


class ITokenService(ABC):
    """Contrato para generación de tokens (por ejemplo, JWT)."""

    @abstractmethod
    def generate_token(self, usuario: Usuario) -> str:
        """Genera un token de acceso para un usuario dado."""
        pass
