"""
Entidad de dominio: Usuario.

Clase pura de Python (dataclass) para gestionar usuarios.
"""
from dataclasses import dataclass
from typing import Optional

from domain.exceptions import DomainValidationError


@dataclass
class Usuario:
    """Entidad de dominio que representa un usuario del sistema."""

    correo: str
    password_hash: str
    rol: str
    compania_id: Optional[int] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        """Normalizar datos."""
        self.correo = self.correo.strip().lower() if isinstance(self.correo, str) else self.correo
        self.rol = self.rol.strip().upper() if isinstance(self.rol, str) else self.rol

    def validar(self) -> None:
        """Validar las reglas de negocio del usuario."""
        if not self.correo:
            raise DomainValidationError("El correo es requerido.")
        if not self.password_hash:
            raise DomainValidationError("La contraseña es requerida.")
        if self.rol not in ["ADMIN", "USUARIO"]:
            raise DomainValidationError("Rol inválido. Debe ser ADMIN o USUARIO.")
        if self.rol == "USUARIO" and not self.compania_id:
            raise DomainValidationError("Un USUARIO estándar debe estar asociado a una compañía.")
