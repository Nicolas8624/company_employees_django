"""
Entidad de dominio: Compania.

Clase pura de Python (dataclass) — NO depende de Django ni del ORM.
Representa el concepto de negocio de una compañía.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Compania:
    """Entidad de dominio que representa una compañía."""

    nombre: str
    direccion: str
    telefono: str
    id: Optional[int] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"Compania(id={self.id}, nombre='{self.nombre}')"
