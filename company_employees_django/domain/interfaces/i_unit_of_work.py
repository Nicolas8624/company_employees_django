"""
Interfaz abstracta para el Unit of Work.

Define el contrato para coordinar transacciones entre
múltiples repositorios. NO depende de Django.
"""
from abc import ABC, abstractmethod

from domain.interfaces.i_compania_repository import ICompaniaRepository
from domain.interfaces.i_empleado_repository import IEmpleadoRepository
from domain.interfaces.i_usuario_repository import IUsuarioRepository


class IUnitOfWork(ABC):
    """Contrato para el Unit of Work."""

    compania_repository: ICompaniaRepository
    empleado_repository: IEmpleadoRepository
    usuario_repository: IUsuarioRepository

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork":
        """Iniciar la transacción."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finalizar la transacción (commit o rollback)."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Confirmar la transacción."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Revertir la transacción."""
        pass
