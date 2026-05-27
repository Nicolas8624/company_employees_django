"""
Entidad de dominio: Empleado.

Clase pura de Python (dataclass) — NO depende de Django ni del ORM.
Representa el concepto de negocio de un empleado.

Incluye reglas de validación de negocio propias de la entidad.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from domain.exceptions import DomainValidationError


@dataclass
class Empleado:
    """Entidad de dominio que representa un empleado."""

    nombre: str
    apellido: str
    correo: str
    cargo: str
    salario: Decimal
    compania_id: int
    id: Optional[int] = None

    def __post_init__(self) -> None:
        """Normalizar datos al crear la entidad."""
        self.nombre = self.nombre.strip() if isinstance(self.nombre, str) else self.nombre
        self.apellido = self.apellido.strip() if isinstance(self.apellido, str) else self.apellido
        self.correo = self.correo.strip().lower() if isinstance(self.correo, str) else self.correo
        self.cargo = self.cargo.strip() if isinstance(self.cargo, str) else self.cargo

    def validar(self) -> None:
        """
        Validar las reglas de negocio del empleado.

        Lanza DomainValidationError si alguna regla no se cumple.
        """
        if not self.nombre:
            raise DomainValidationError("El nombre del empleado no puede estar vacío.")

        if not self.apellido:
            raise DomainValidationError("El apellido del empleado no puede estar vacío.")

        if not self.correo:
            raise DomainValidationError("El correo del empleado no puede estar vacío.")

        if not self.cargo:
            raise DomainValidationError("El cargo del empleado no puede estar vacío.")

        if self.salario is None or self.salario <= 0:
            raise DomainValidationError("El salario debe ser mayor a cero.")

        if self.compania_id is None or self.compania_id <= 0:
            raise DomainValidationError("El ID de compañía debe ser un número positivo.")

    def nombre_completo(self) -> str:
        """Obtener el nombre completo del empleado."""
        return f"{self.nombre} {self.apellido}"

    def __str__(self) -> str:
        return f"Empleado(id={self.id}, nombre='{self.nombre_completo()}')"
