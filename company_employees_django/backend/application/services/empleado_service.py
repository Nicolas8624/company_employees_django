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

    def _validar_negocio_empleado(self, empleado: Empleado, skip_correo: bool = False) -> None:
        """Validar reglas de negocio usando repositorios."""
        from domain.exceptions import DomainValidationError
        errores = []

        # Validar si compañía existe
        compania = self._uow.compania_repository.get_by_id(empleado.compania_id)
        if not compania:
            errores.append({"campo": "compania_id", "detalle": f"La compañía con ID {empleado.compania_id} no existe."})

        # Validar correo único (solo si no estamos ignorando la validación del correo)
        if not skip_correo:
            existentes = self._uow.empleado_repository.find_by_condition(correo=empleado.correo)
            # Si hay alguno y el ID no coincide con el que estamos actualizando
            for e in existentes:
                if empleado.id is None or e.id != empleado.id:
                    errores.append({"campo": "correo", "detalle": "El correo ya está registrado."})
                    break

        if errores:
            raise DomainValidationError("Error de validacion", errores=errores)

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
            self._validar_negocio_empleado(empleado)

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
            self._validar_negocio_empleado(existing)
            
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

    def bulk_create_empleados(self, empleados_data: List[Dict[str, Any]]) -> List[Empleado]:
        """Crear múltiples empleados usando bulk."""
        logger.info("Creando %s empleados en bulk", len(empleados_data))
        with self._uow:
            empleados_a_crear = []
            for data in empleados_data:
                empleado = Empleado(
                    nombre=data["nombre"],
                    apellido=data["apellido"],
                    correo=data["correo"],
                    cargo=data["cargo"],
                    salario=data["salario"],
                    compania_id=data["compania_id"]
                )
                empleado.validar()
                self._validar_negocio_empleado(empleado, skip_correo=True) # Validaremos correos todos juntos
                empleados_a_crear.append(empleado)
            
            # Validación bulk de correos
            from domain.exceptions import DomainValidationError
            correos_nuevos = [e.correo for e in empleados_a_crear]
            if len(correos_nuevos) != len(set(correos_nuevos)):
                raise DomainValidationError("Error de validacion", errores=[{"campo": "correo", "detalle": "Hay correos duplicados en la lista enviada."}])
                
            for correo in correos_nuevos:
                if self._uow.empleado_repository.find_by_condition(correo=correo):
                    raise DomainValidationError("Error de validacion", errores=[{"campo": "correo", "detalle": f"El correo {correo} ya está registrado."}])
            
            created = self._uow.empleado_repository.bulk_create(empleados_a_crear)
            self._uow.commit()
            return created

    def patch_empleado(self, empleado_id: int, data: Dict[str, Any]) -> Optional[Empleado]:
        """Actualización parcial de un empleado."""
        logger.info("Patching empleado con ID: %s", empleado_id)
        with self._uow:
            existing = self._uow.empleado_repository.get_by_id(empleado_id)
            if not existing:
                return None
            
            # Apply partial updates
            if "nombre" in data: existing.nombre = data["nombre"]
            if "apellido" in data: existing.apellido = data["apellido"]
            if "correo" in data: existing.correo = data["correo"]
            if "cargo" in data: existing.cargo = data["cargo"]
            if "salario" in data: existing.salario = data["salario"]
            if "compania_id" in data: existing.compania_id = data["compania_id"]
            
            existing.__post_init__()
            existing.validar()
            self._validar_negocio_empleado(existing)
            
            updated = self._uow.empleado_repository.patch(empleado_id, data)
            self._uow.commit()
            return updated

    def delete_many_empleados(self, ids: List[int]) -> int:
        """Eliminar múltiples empleados."""
        logger.info("Eliminando %s empleados en bulk", len(ids))
        with self._uow:
            count = self._uow.empleado_repository.delete_many(ids)
            self._uow.commit()
            return count

    def get_paginated_empleados(
        self, page: int = 1, size: int = 10, sort_by: str = "", sort_dir: str = "asc", search: str = ""
    ) -> Dict[str, Any]:
        """Obtener lista paginada de empleados."""
        logger.info("Obteniendo empleados paginados: page=%s, size=%s", page, size)
        with self._uow:
            return self._uow.empleado_repository.get_paginated(
                page=page, size=size, sort_by=sort_by, sort_dir=sort_dir, search=search
            )
