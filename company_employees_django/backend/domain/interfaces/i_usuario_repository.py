"""
Interfaz del Repositorio de Usuarios.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from domain.entities.usuario import Usuario


class IUsuarioRepository(ABC):
    """Contrato genérico para persistencia de Usuarios."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def get_all(self) -> List[Usuario]:
        pass

    @abstractmethod
    def create(self, entity: Usuario) -> Usuario:
        pass

    @abstractmethod
    def update(self, entity_id: int, entity_data: Dict[str, Any]) -> Optional[Usuario]:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass

    @abstractmethod
    def find_by_correo(self, correo: str) -> Optional[Usuario]:
        """Buscar un usuario por su correo electrónico."""
        pass
