"""
Entidad de dominio: Compania.

Clase pura de Python (dataclass) — NO depende de Django ni del ORM.
Representa el concepto de negocio de una compañía.

Incluye reglas de validación de negocio propias de la entidad.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from domain.exceptions import DomainValidationError


@dataclass
class Compania:
    """Entidad de dominio que representa una compañía."""

    nombre: str
    direccion: str
    telefono: str
    id: Optional[int] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Normalizar datos al crear la entidad."""
        self.nombre = self.nombre.strip() if isinstance(self.nombre, str) else self.nombre
        self.direccion = self.direccion.strip() if isinstance(self.direccion, str) else self.direccion
        self.telefono = self.telefono.strip() if isinstance(self.telefono, str) else self.telefono

    def validar(self) -> None:
        """
        Validar las reglas de negocio de la compañía.

        Lanza DomainValidationError si alguna regla no se cumple.
        """
        if not self.nombre:
            raise DomainValidationError("El nombre de la compañía no puede estar vacío.")

        if not self.direccion:
            raise DomainValidationError("La dirección de la compañía no puede estar vacía.")

        if not self.telefono:
            raise DomainValidationError("El teléfono de la compañía no puede estar vacío.")

    def __str__(self) -> str:
        return f"Compania(id={self.id}, nombre='{self.nombre}')"
