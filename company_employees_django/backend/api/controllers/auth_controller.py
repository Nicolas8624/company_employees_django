"""
Controlador de Autenticación.
"""
import logging

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api.permissions.permissions import IsAuthenticatedUser

from infrastructure.service_locator import ServiceLocator
from domain.exceptions import DomainValidationError

logger = logging.getLogger(__name__)


class RegistroController(APIView):
    """
    POST /api/auth/registro -> Registrar usuario nuevo
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        logger.info("POST /api/auth/registro")
        try:
            service = ServiceLocator.get_auth_service()
            result = service.registro(request.data)
            return Response(result, status=status.HTTP_201_CREATED)
        except DomainValidationError as e:
            return Response({"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error interno: {str(e)}")
            return Response({"error": "Error interno"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginController(APIView):
    """
    POST /api/auth/login -> Iniciar sesión y recibir token
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        logger.info("POST /api/auth/login")
        try:
            correo = request.data.get("correo")
            password = request.data.get("password")
            
            if not correo or not password:
                return Response(
                    {"mensaje": "Error de autenticación", "errores": [{"campo": "credenciales", "detalle": "Correo y contraseña son requeridos"}]},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            service = ServiceLocator.get_auth_service()
            result = service.login(correo, password)
            return Response(result, status=status.HTTP_200_OK)
        except DomainValidationError as e:
            return Response({"mensaje": e.mensaje, "errores": getattr(e, 'errores', [])}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error interno: {str(e)}")
            return Response({"error": "Error interno"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerfilController(APIView):
    """
    GET /api/auth/perfil -> Obtener el perfil del usuario logueado
    """
    permission_classes = [IsAuthenticatedUser]

    def get(self, request: Request) -> Response:
        logger.info("GET /api/auth/perfil")
        user = request.user
        # request.user es un UsuarioAutenticado inyectado por JwtCustomAuthentication
        return Response({
            "id": user.id,
            "correo": user.correo,
            "rol": user.rol,
            "ciudad": user.ciudad,
            "compania_id": user.compania_id,
        }, status=status.HTTP_200_OK)

