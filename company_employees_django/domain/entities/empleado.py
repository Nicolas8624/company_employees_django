"""
Entidad de dominio: Empleado.

Clase pura de Python (dataclass) — NO depende de Django ni del ORM.
Representa el concepto de negocio de un empleado.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


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

    def __str__(self) -> str:
        return f"Empleado(id={self.id}, nombre='{self.nombre} {self.apellido}')"
