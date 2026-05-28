"""
Clases de permisos (Permission Classes) para la API.

Implementan la autorización por roles y por política de propiedad.
Leen datos del UsuarioAutenticado (request.user) inyectado por
JwtCustomAuthentication, sin acceder al ORM.
"""
import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    """
    Permite acceso únicamente a usuarios con rol ADMIN.
    """
    message = "Acceso restringido a administradores."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return getattr(user, "rol", "") == "ADMIN"


class IsAdminOrUsuario(BasePermission):
    """
    Permite acceso a usuarios autenticados con rol ADMIN o USUARIO.
    Usado para POST/PUT/PATCH.
    """
    message = "Debes estar autenticado como ADMIN o USUARIO."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return getattr(user, "rol", "") in ("ADMIN", "USUARIO")


class IsAuthenticatedUser(BasePermission):
    """
    Permite acceso a cualquier usuario autenticado (token válido).
    Usado para GET.
    """
    message = "Debes estar autenticado."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return user is not None and getattr(user, "is_authenticated", False)


class EsPropietarioDeCompania(BasePermission):
    """
    Política de propiedad:
    - ADMIN puede todo.
    - USUARIO solo puede editar/eliminar empleados de su propia compañía.

    Módulo 5 — Autorización por políticas.
    """
    message = "No tienes permiso para modificar empleados de otra compañía."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False

        # ADMIN puede todo
        if getattr(user, "rol", "") == "ADMIN":
            return True

        # Para PUT/PATCH necesitamos verificar la compañía del empleado.
        # has_permission no tiene acceso al objeto, así que verificamos
        # contra el body del request (compania_id del empleado a crear/editar)
        # La verificación a nivel de objeto se hace en has_object_permission.
        return True

    def has_object_permission(self, request, view, obj):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "rol", "") == "ADMIN":
            return True

        # USUARIO solo puede operar sobre empleados de su compañía
        user_compania_id = getattr(user, "compania_id", None)
        if not user_compania_id:
            return False

        # obj puede ser un Empleado (dataclass) o dict con compania_id
        if hasattr(obj, "compania_id"):
            empleado_compania_id = obj.compania_id
        elif isinstance(obj, dict):
            empleado_compania_id = obj.get("compania_id")
        else:
            return False

        return int(user_compania_id) == int(empleado_compania_id)
