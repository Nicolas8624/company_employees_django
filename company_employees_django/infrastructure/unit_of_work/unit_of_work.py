"""
Implementación concreta del Unit of Work.

Usa transaction.atomic de Django para coordinar transacciones
entre múltiples repositorios. Es el ÚNICO responsable de
commit y rollback.
"""
import logging

from django.db import transaction

from domain.interfaces.i_unit_of_work import IUnitOfWork
from infrastructure.repositories.compania_repository import CompaniaRepository
from infrastructure.repositories.empleado_repository import EmpleadoRepository

logger = logging.getLogger(__name__)


class UnitOfWork(IUnitOfWork):
    """
    Unit of Work concreto usando transaction.atomic de Django.

    Uso:
        with UnitOfWork() as uow:
            uow.compania_repository.create(...)
            uow.empleado_repository.create(...)
            uow.commit()
        # Si ocurre una excepción, rollback automático
    """

    def __init__(self) -> None:
        self._compania_repository = CompaniaRepository()
        self._empleado_repository = EmpleadoRepository()
        self._atomic = None

    @property
    def compania_repository(self) -> CompaniaRepository:
        """Acceso al repositorio de compañías."""
        return self._compania_repository

    @property
    def empleado_repository(self) -> EmpleadoRepository:
        """Acceso al repositorio de empleados."""
        return self._empleado_repository

    def __enter__(self) -> "UnitOfWork":
        """Iniciar la transacción con transaction.atomic."""
        logger.info("UnitOfWork: Iniciando transacción")
        self._atomic = transaction.atomic()
        self._atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Finalizar la transacción.
        Si hubo excepción, Django hace rollback automático.
        """
        if exc_type is not None:
            logger.error(
                "UnitOfWork: ROLLBACK — Error tipo=%s, mensaje=%s",
                exc_type.__name__, str(exc_val)
            )
        self._atomic.__exit__(exc_type, exc_val, exc_tb)

    def commit(self) -> None:
        """
        Confirmar la transacción.

        En Django con transaction.atomic, el commit ocurre automáticamente
        al salir del bloque 'with' sin excepciones. Este método existe
        para mantener compatibilidad con la interfaz IUnitOfWork y para logging.
        """
        logger.info("UnitOfWork: COMMIT — Transacción confirmada exitosamente")

    def rollback(self) -> None:
        """
        Revertir la transacción.

        En Django con transaction.atomic, el rollback ocurre automáticamente
        al lanzar una excepción dentro del bloque 'with'.
        """
        logger.warning("UnitOfWork: ROLLBACK — Revirtiendo transacción")
        raise transaction.TransactionManagementError(
            "Rollback forzado por el UnitOfWork"
        )
