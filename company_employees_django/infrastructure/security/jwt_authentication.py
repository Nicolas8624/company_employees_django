"""
Backend de autenticación JWT personalizado.

Simplejwt espera que el token apunte a un User model de Django.
Nosotros usamos nuestra propia entidad de dominio Usuario
(en Infrastructure, detrás de interfaces del dominio).

Este backend lee los claims del JWT y construye un objeto
autenticado simple, sin depender de django.contrib.auth.User.
"""
import logging

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

logger = logging.getLogger(__name__)


class UsuarioAutenticado:
    """
    Objeto ligero que representa al usuario autenticado.
    No es un modelo Django — es un POPO inyectado en request.user.
    """

    def __init__(self, payload: dict):
        self.id = payload.get("user_id")
        self.correo = payload.get("correo", "")
        self.rol = payload.get("rol", "")
        self.compania_id = payload.get("compania_id")
        self.is_authenticated = True


class JwtCustomAuthentication(BaseAuthentication):
    """
    Lee el header Authorization: Bearer <token>,
    valida la firma JWT y devuelve (UsuarioAutenticado, payload).
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None  # no intenta autenticar — deja pasar a otros backends

        raw_token = auth_header.split(" ", 1)[1]

        try:
            validated = AccessToken(raw_token)
        except TokenError as e:
            logger.warning("JWT inválido: %s", str(e))
            raise AuthenticationFailed(f"Token inválido: {str(e)}")

        payload = validated.payload
        user = UsuarioAutenticado(payload)
        return (user, payload)

    def authenticate_header(self, request):
        return 'Bearer'
