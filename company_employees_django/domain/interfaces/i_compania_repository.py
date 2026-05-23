"""
Interfaz abstracta para el repositorio de Compañías.

Define el contrato que debe cumplir cualquier implementación
de persistencia de compañías. NO depende de Django.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from domain.entities.compania import Compania


class ICompaniaRepository(ABC):
    """Contrato para el repositorio de compañías."""

    @abstractmethod
    def get_all(self) -> List[Compania]:
        """Obtener todas las compañías."""
        pass

    @abstractmethod
    def get_by_id(self, compania_id: int) -> Optional[Compania]:
        """Obtener una compañía por su ID."""
        pass

    @abstractmethod
    def create(self, compania: Compania) -> Compania:
        """Crear una nueva compañía. NO hace commit."""
        pass

    @abstractmethod
    def update(self, compania_id: int, data: Dict[str, Any]) -> Optional[Compania]:
        """Actualizar una compañía existente. NO hace commit."""
        pass

    @abstractmethod
    def delete(self, compania_id: int) -> bool:
        """Eliminar una compañía. NO hace commit."""
        pass

    @abstractmethod
    def find_by_condition(self, **kwargs: Any) -> List[Compania]:
        """Buscar compañías por condición."""
        pass
