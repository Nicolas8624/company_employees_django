"""
Servicio de aplicación para Compañías.

Contiene toda la lógica de negocio relacionada con compañías.
Los controllers delegan aquí. Este servicio usa el UnitOfWork
para coordinar la persistencia.
"""
import logging
from typing import Any, Dict, List, Optional

from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from domain.interfaces.i_unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class CompaniaService:
    """Servicio de aplicación para operaciones con compañías."""

    def __init__(self, unit_of_work: IUnitOfWork) -> None:
        self._uow = unit_of_work

    def get_all_companias(self) -> List[Compania]:
        """Obtener todas las compañías."""
        logger.info("Obteniendo todas las compañías")
        with self._uow:
            return self._uow.compania_repository.get_all()

    def get_compania_by_id(self, compania_id: int) -> Optional[Compania]:
        """Obtener una compañía por su ID."""
        logger.info("Obteniendo compañía con ID: %s", compania_id)
        with self._uow:
            compania = self._uow.compania_repository.get_by_id(compania_id)
            if compania is None:
                logger.warning("Compañía con ID %s no encontrada", compania_id)
            return compania

    def create_compania(self, data: Dict[str, Any]) -> Compania:
        """Crear una nueva compañía."""
        logger.info("Creando nueva compañía: %s", data.get("nombre", ""))
        with self._uow:
            compania = Compania(
                nombre=data["nombre"],
                direccion=data["direccion"],
                telefono=data["telefono"],
            )
            created = self._uow.compania_repository.create(compania)
            self._uow.commit()
            logger.info("Compañía creada exitosamente con ID: %s", created.id)
            return created

    def update_compania(
        self, compania_id: int, data: Dict[str, Any]
    ) -> Optional[Compania]:
        """Actualizar una compañía existente."""
        logger.info("Actualizando compañía con ID: %s", compania_id)
        with self._uow:
            updated = self._uow.compania_repository.update(compania_id, data)
            if updated is None:
                logger.warning("Compañía con ID %s no encontrada para actualizar", compania_id)
                return None
            self._uow.commit()
            logger.info("Compañía con ID %s actualizada exitosamente", compania_id)
            return updated

    def delete_compania(self, compania_id: int) -> bool:
        """Eliminar una compañía."""
        logger.info("Eliminando compañía con ID: %s", compania_id)
        with self._uow:
            deleted = self._uow.compania_repository.delete(compania_id)
            if not deleted:
                logger.warning("Compañía con ID %s no encontrada para eliminar", compania_id)
                return False
            self._uow.commit()
            logger.info("Compañía con ID %s eliminada exitosamente", compania_id)
            return True

    def get_empleados_by_compania(self, compania_id: int) -> Optional[List[Empleado]]:
        """Obtener todos los empleados de una compañía."""
        logger.info("Obteniendo empleados de la compañía con ID: %s", compania_id)
        with self._uow:
            compania = self._uow.compania_repository.get_by_id(compania_id)
            if compania is None:
                logger.warning("Compañía con ID %s no encontrada", compania_id)
                return None
            return self._uow.empleado_repository.get_by_compania(compania_id)

    def create_compania_con_empleados(
        self, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crear una compañía con múltiples empleados en una sola transacción.

        Si falla la creación de cualquier empleado, se hace rollback completo
        y no se guarda nada (ni la compañía ni los empleados).
        """
        logger.info("=== INICIO TRANSACCIÓN: Crear compañía con empleados ===")
        logger.info("Compañía: %s | Empleados: %d",
                     data.get("nombre", ""), len(data.get("empleados", [])))

        with self._uow:
            try:
                # Crear la compañía
                compania = Compania(
                    nombre=data["nombre"],
                    direccion=data["direccion"],
                    telefono=data["telefono"],
                )
                compania_creada = self._uow.compania_repository.create(compania)
                logger.info("Compañía creada en transacción: ID=%s", compania_creada.id)

                # Crear los empleados
                empleados_creados: List[Empleado] = []
                for emp_data in data.get("empleados", []):
                    empleado = Empleado(
                        nombre=emp_data["nombre"],
                        apellido=emp_data["apellido"],
                        correo=emp_data["correo"],
                        cargo=emp_data["cargo"],
                        salario=emp_data["salario"],
                        compania_id=compania_creada.id,
                    )
                    empleado_creado = self._uow.empleado_repository.create(empleado)
                    empleados_creados.append(empleado_creado)
                    logger.info("Empleado creado en transacción: ID=%s, nombre=%s %s",
                                empleado_creado.id, empleado_creado.nombre,
                                empleado_creado.apellido)

                # Commit global de toda la transacción
                self._uow.commit()
                logger.info("=== COMMIT EXITOSO: Compañía + %d empleados ===",
                            len(empleados_creados))

                return {
                    "compania": compania_creada,
                    "empleados": empleados_creados,
                }

            except Exception as e:
                # Rollback automático por transaction.atomic
                logger.error("=== ROLLBACK: Error en transacción — %s ===", str(e))
                raise
