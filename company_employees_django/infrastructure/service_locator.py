"""
Service Locator — Composition Root.

Punto central de composición que resuelve las dependencias
entre capas. Actúa como factory para crear los servicios
de aplicación con sus dependencias inyectadas.

La capa API usa este módulo para obtener servicios SIN conocer
las implementaciones concretas de Infrastructure.

Esto desacopla la capa API de la capa Infrastructure,
cumpliendo estrictamente con Onion Architecture.
"""
import logging

from application.services.compania_service import CompaniaService
from application.services.empleado_service import EmpleadoService
from domain.interfaces.i_unit_of_work import IUnitOfWork
from infrastructure.unit_of_work.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ServiceLocator:
    """
    Localizador de servicios — Composition Root del proyecto.

    Centraliza la creación de servicios con sus dependencias
    concretas. Los controllers solo conocen esta clase y las
    interfaces del dominio, NO las implementaciones de infrastructure.

    Uso en controllers:
        service = ServiceLocator.get_compania_service()
        companias = service.get_all_companias()
    """

    @staticmethod
    def get_unit_of_work() -> IUnitOfWork:
        """
        Obtener una instancia del Unit of Work.

        Retorna la implementación concreta (UnitOfWork de Django)
        pero tipada como la interfaz IUnitOfWork.
        """
        return UnitOfWork()

    @staticmethod
    def get_compania_service() -> CompaniaService:
        """
        Obtener una instancia del servicio de compañías.

        Crea el servicio con el UnitOfWork inyectado.
        """
        uow = ServiceLocator.get_unit_of_work()
        return CompaniaService(unit_of_work=uow)

    @staticmethod
    def get_empleado_service() -> EmpleadoService:
        """
        Obtener una instancia del servicio de empleados.

        Crea el servicio con el UnitOfWork inyectado.
        """
        uow = ServiceLocator.get_unit_of_work()
        return EmpleadoService(unit_of_work=uow)
