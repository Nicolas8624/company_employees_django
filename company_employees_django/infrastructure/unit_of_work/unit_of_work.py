"""
Implementación concreta del Unit of Work.

Usa transaction.atomic de Django para coordinar transacciones
entre múltiples repositorios. Es el ÚNICO responsable de
commit y rollback.

El flag _committed provee claridad semántica: indica que la
operación de negocio fue completada exitosamente dentro del
bloque transaccional.
"""
import logging

from django.db import transaction

from domain.interfaces.i_unit_of_work import IUnitOfWork
from infrastructure.repositories.compania_repository import CompaniaRepository
from infrastructure.repositories.empleado_repository import EmpleadoRepository
from infrastructure.repositories.usuario_repository import UsuarioRepository

logger = logging.getLogger(__name__)


class UnitOfWork(IUnitOfWork):
    """
    Unit of Work concreto usando transaction.atomic de Django.

    Uso:
        with UnitOfWork() as uow:
            uow.compania_repository.create(...)
            uow.empleado_repository.create(...)
            uow.usuario_repository.create(...)
            uow.commit()
        # Si ocurre una excepción, rollback automático

    El flag _committed garantiza que el servicio llamó commit()
    explícitamente antes de que la transacción se confirme.
    Si no se llama commit(), se registra un warning en el log.
    """

    def __init__(self) -> None:
        self._compania_repository = CompaniaRepository()
        self._empleado_repository = EmpleadoRepository()
        self._usuario_repository = UsuarioRepository()
        self._atomic = None
        self._committed: bool = False

    @property
    def compania_repository(self) -> CompaniaRepository:
        """Acceso al repositorio de compañías."""
        return self._compania_repository

    @property
    def empleado_repository(self) -> EmpleadoRepository:
        """Acceso al repositorio de empleados."""
        return self._empleado_repository

    @property
    def usuario_repository(self) -> UsuarioRepository:
        """Acceso al repositorio de usuarios."""
        return self._usuario_repository

    def __enter__(self) -> "UnitOfWork":
        """Iniciar la transacción con transaction.atomic."""
        logger.info("UnitOfWork: Iniciando transacción")
        self._committed = False
        self._atomic = transaction.atomic()
        self._atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Finalizar la transacción.

        - Si hubo excepción: Django hace rollback automático.
        - Si no hubo excepción pero no se llamó commit(): warning de log.
        - Si se llamó commit() y no hubo excepción: Django confirma al salir.
        """
        if exc_type is not None:
            logger.error(
                "UnitOfWork: ROLLBACK — Error tipo=%s, mensaje=%s",
                exc_type.__name__, str(exc_val)
            )
        elif not self._committed:
            logger.warning(
                "UnitOfWork: Transacción finalizada sin llamar commit(). "
                "Esto puede indicar un flujo incompleto."
            )
        self._atomic.__exit__(exc_type, exc_val, exc_tb)

    def commit(self) -> None:
        """
        Confirmar la transacción.

        Marca el flag _committed como True para indicar que la operación
        de negocio fue completada correctamente. En Django con
        transaction.atomic, el commit real ocurre al salir del bloque
        'with' sin excepciones. Este método proporciona:

        1. Señal semántica de que la operación terminó con éxito.
        2. Logging del commit para trazabilidad.
        3. Detección de flujos donde no se llama commit().
        """
        self._committed = True
        logger.info("UnitOfWork: COMMIT — Transacción marcada como confirmada")

    def rollback(self) -> None:
        """
        Revertir la transacción.

        En Django con transaction.atomic, el rollback ocurre automáticamente
        al lanzar una excepción dentro del bloque 'with'. Este método
        fuerza el rollback explícitamente lanzando una excepción.
        """
        self._committed = False
        logger.warning("UnitOfWork: ROLLBACK — Revirtiendo transacción")
        raise transaction.TransactionManagementError(
            "Rollback forzado por el UnitOfWork"
        )
