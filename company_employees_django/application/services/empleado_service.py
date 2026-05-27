"""
Servicio de aplicación para Empleados.

Contiene toda la lógica de negocio relacionada con empleados.
Los controllers delegan aquí. Este servicio usa el UnitOfWork
para coordinar la persistencia.

Las validaciones de negocio se delegan a las entidades de dominio.
"""
import logging
from typing import Any, Dict, List, Optional

from domain.entities.empleado import Empleado
from domain.interfaces.i_unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class EmpleadoService:
    """Servicio de aplicación para operaciones con empleados."""

    def __init__(self, unit_of_work: IUnitOfWork) -> None:
        self._uow = unit_of_work

    def get_all_empleados(self) -> List[Empleado]:
        """Obtener todos los empleados."""
        logger.info("Obteniendo todos los empleados")
        with self._uow:
            return self._uow.empleado_repository.get_all()

    def get_empleado_by_id(self, empleado_id: int) -> Optional[Empleado]:
        """Obtener un empleado por su ID."""
        logger.info("Obteniendo empleado con ID: %s", empleado_id)
        with self._uow:
            empleado = self._uow.empleado_repository.get_by_id(empleado_id)
            if empleado is None:
                logger.warning("Empleado con ID %s no encontrado", empleado_id)
            return empleado

    def create_empleado(self, data: Dict[str, Any]) -> Empleado:
        """
        Crear un nuevo empleado.

        La entidad de dominio valida las reglas de negocio
        antes de persistir.
        """
        logger.info("Creando nuevo empleado: %s %s",
                     data.get("nombre", ""), data.get("apellido", ""))
        with self._uow:
            empleado = Empleado(
                nombre=data["nombre"],
                apellido=data["apellido"],
                correo=data["correo"],
                cargo=data["cargo"],
                salario=data["salario"],
                compania_id=data["compania_id"],
            )
            # Validación de reglas de negocio en el dominio
            empleado.validar()

            created = self._uow.empleado_repository.create(empleado)
            self._uow.commit()
            logger.info("Empleado creado exitosamente con ID: %s", created.id)
            return created

    def update_empleado(
        self, empleado_id: int, data: Dict[str, Any]
    ) -> Optional[Empleado]:
        """Actualizar un empleado existente."""
        logger.info("Actualizando empleado con ID: %s", empleado_id)
        with self._uow:
            existing = self._uow.empleado_repository.get_by_id(empleado_id)
            if existing is None:
                logger.warning("Empleado con ID %s no encontrado para actualizar", empleado_id)
                return None
            
            if "nombre" in data:
                existing.nombre = data["nombre"]
            if "apellido" in data:
                existing.apellido = data["apellido"]
            if "correo" in data:
                existing.correo = data["correo"]
            if "cargo" in data:
                existing.cargo = data["cargo"]
            if "salario" in data:
                existing.salario = data["salario"]
            if "compania_id" in data:
                existing.compania_id = data["compania_id"]
                
            existing.__post_init__()
            existing.validar()
            
            updated = self._uow.empleado_repository.update(empleado_id, {
                "nombre": existing.nombre,
                "apellido": existing.apellido,
                "correo": existing.correo,
                "cargo": existing.cargo,
                "salario": existing.salario,
                "compania_id": existing.compania_id,
            })
            self._uow.commit()
            logger.info("Empleado con ID %s actualizado exitosamente", empleado_id)
            return updated

    def delete_empleado(self, empleado_id: int) -> bool:
        """Eliminar un empleado."""
        logger.info("Eliminando empleado con ID: %s", empleado_id)
        with self._uow:
            deleted = self._uow.empleado_repository.delete(empleado_id)
            if not deleted:
                logger.warning("Empleado con ID %s no encontrado para eliminar", empleado_id)
                return False
            self._uow.commit()
            logger.info("Empleado con ID %s eliminado exitosamente", empleado_id)
            return True
