"""
Implementación de ITokenService usando djangorestframework-simplejwt.
"""
from rest_framework_simplejwt.tokens import RefreshToken

from domain.entities.usuario import Usuario
from domain.interfaces.i_token_service import ITokenService


class JwtTokenService(ITokenService):
    """Implementación de generación de JWT."""

    def generate_token(self, usuario: Usuario) -> str:
        # Usamos un usuario "falso" o inyectamos claims directamente
        refresh = RefreshToken()
        
        # Inyectar claims personalizados
        refresh["user_id"] = usuario.id
        refresh["correo"] = usuario.correo
        refresh["rol"] = usuario.rol
        if usuario.compania_id:
            refresh["compania_id"] = usuario.compania_id

        # Retornamos solo el access_token para este requerimiento simple
        return str(refresh.access_token)
