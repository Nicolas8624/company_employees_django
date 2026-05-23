"""
Interfaz abstracta para el repositorio de Empleados.

Define el contrato que debe cumplir cualquier implementación
de persistencia de empleados. NO depende de Django.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from domain.entities.empleado import Empleado


class IEmpleadoRepository(ABC):
    """Contrato para el repositorio de empleados."""

    @abstractmethod
    def get_all(self) -> List[Empleado]:
        """Obtener todos los empleados."""
        pass

    @abstractmethod
    def get_by_id(self, empleado_id: int) -> Optional[Empleado]:
        """Obtener un empleado por su ID."""
        pass

    @abstractmethod
    def create(self, empleado: Empleado) -> Empleado:
        """Crear un nuevo empleado. NO hace commit."""
        pass

    @abstractmethod
    def update(self, empleado_id: int, data: Dict[str, Any]) -> Optional[Empleado]:
        """Actualizar un empleado existente. NO hace commit."""
        pass

    @abstractmethod
    def delete(self, empleado_id: int) -> bool:
        """Eliminar un empleado. NO hace commit."""
        pass

    @abstractmethod
    def find_by_condition(self, **kwargs: Any) -> List[Empleado]:
        """Buscar empleados por condición."""
        pass

    @abstractmethod
    def get_by_compania(self, compania_id: int) -> List[Empleado]:
        """Obtener todos los empleados de una compañía."""
        pass
