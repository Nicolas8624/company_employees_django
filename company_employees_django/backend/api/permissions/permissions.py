"""
Clases de permisos (Permission Classes) para la API.

Implementan la autorización por roles y por política de propiedad.
Leen datos del UsuarioAutenticado (request.user) inyectado por
JwtCustomAuthentication, sin acceder al ORM.
"""
import logging
import unicodedata

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
    - USUARIO solo puede editar/eliminar/crear empleados de su propia compañía.

    Módulo 5 — Autorización por políticas.
    """
    message = "No tienes permiso para operar sobre empleados de otra compañía o moverlos de compañía."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False

        # ADMIN puede todo
        if getattr(user, "rol", "") == "ADMIN":
            return True

        # Para USUARIO, validamos que si intenta crear o modificar con compania_id, coincida con la propia.
        user_compania_id = getattr(user, "compania_id", None)
        if user_compania_id is None:
            return False

        # Validación para creación masiva (bulk): "empleados" es una lista de objetos
        empleados_bulk = request.data.get("empleados")
        if isinstance(empleados_bulk, list):
            for emp in empleados_bulk:
                emp_compania_id = emp.get("compania_id") if isinstance(emp, dict) else None
                if emp_compania_id is not None:
                    try:
                        if int(emp_compania_id) != int(user_compania_id):
                            logger.warning(
                                "Política bulk: usuario %s intenta crear empleado en compañía %s (la suya: %s)",
                                getattr(user, "correo", "?"), emp_compania_id, user_compania_id
                            )
                            return False
                    except (ValueError, TypeError):
                        return False
            return True

        # Validación para creación individual: "compania_id" en el body
        req_compania_id = request.data.get("compania_id")
        if req_compania_id is not None:
            try:
                if int(req_compania_id) != int(user_compania_id):
                    return False
            except (ValueError, TypeError):
                return False

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


class PoliticaAdminCiudad(BasePermission):
    """
    Módulo 5 - Políticas / Claims (claim JWT: ciudad):

    - ADMIN de Medellín (claim ciudad = medellin / medellín): CRUD completo.
    - ADMIN de Bogotá (claim ciudad = bogota / bogotá): GET, POST, PUT y PATCH;
      no puede eliminar (DELETE).
    - Otros roles: esta política no aplica restricciones adicionales.
    """
    message = (
        "Acceso restringido: los administradores de Bogotá no pueden eliminar recursos "
        "(operación DELETE no permitida)."
    )

    @staticmethod
    def _normalizar_ciudad(ciudad: str) -> str:
        """Normaliza el string de ciudad eliminando tildes y convirtiéndolo a minúsculas."""
        nfkd = unicodedata.normalize("NFD", ciudad)
        return "".join(c for c in nfkd if unicodedata.category(c) != "Mn").lower().strip()

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "rol", "") != "ADMIN":
            return True

        ciudad = self._normalizar_ciudad(getattr(user, "ciudad", "") or "")

        if ciudad == "bogota" and request.method == "DELETE":
            logger.warning(
                "Acceso bloqueado por política: Admin de Bogotá intentando DELETE"
            )
            return False

        return True
