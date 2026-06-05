"""
Servicio de aplicación para Compañías.

Contiene toda la lógica de negocio relacionada con compañías.
Los controllers delegan aquí. Este servicio usa el UnitOfWork
para coordinar la persistencia.

Las validaciones de negocio se delegan a las entidades de dominio.
"""
import logging
from typing import Any, Dict, List, Optional

from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from domain.exceptions import EntityNotFoundError
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
        """
        Crear una nueva compañía.

        La entidad de dominio valida las reglas de negocio
        antes de persistir.
        """
        logger.info("Creando nueva compañía: %s", data.get("nombre", ""))
        with self._uow:
            compania = Compania(
                nombre=data["nombre"],
                direccion=data["direccion"],
                telefono=data["telefono"],
            )
            # Validación de reglas de negocio en el dominio
            compania.validar()

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
            existing = self._uow.compania_repository.get_by_id(compania_id)
            if existing is None:
                logger.warning("Compañía con ID %s no encontrada para actualizar", compania_id)
                return None
            
            if "nombre" in data:
                existing.nombre = data["nombre"]
            if "direccion" in data:
                existing.direccion = data["direccion"]
            if "telefono" in data:
                existing.telefono = data["telefono"]
                
            existing.__post_init__()
            existing.validar()
            
            updated = self._uow.compania_repository.update(compania_id, {
                "nombre": existing.nombre,
                "direccion": existing.direccion,
                "telefono": existing.telefono,
            })
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

        Las validaciones de negocio se ejecutan en las entidades de dominio
        ANTES de intentar persistir.
        """
        logger.info("=== INICIO TRANSACCIÓN: Crear compañía con empleados ===")
        logger.info("Compañía: %s | Empleados: %d",
                     data.get("nombre", ""), len(data.get("empleados", [])))

        with self._uow:
            try:
                # Crear y validar la compañía
                compania = Compania(
                    nombre=data["nombre"],
                    direccion=data["direccion"],
                    telefono=data["telefono"],
                )
                compania.validar()

                compania_creada = self._uow.compania_repository.create(compania)
                logger.info("Compañía creada en transacción: ID=%s", compania_creada.id)

                # Crear y validar los empleados
                empleados_creados: List[Empleado] = []
                
                # Pre-validar todos los correos para evitar fallas a mitad
                correos_empleados = [emp_data["correo"] for emp_data in data.get("empleados", [])]
                if len(correos_empleados) != len(set(correos_empleados)):
                    from domain.exceptions import DomainValidationError
                    raise DomainValidationError("Error de validacion", errores=[{"campo": "correo", "detalle": "Hay correos duplicados en la lista enviada."}])
                
                for correo in correos_empleados:
                    if self._uow.empleado_repository.find_by_condition(correo=correo):
                        from domain.exceptions import DomainValidationError
                        raise DomainValidationError("Error de validacion", errores=[{"campo": "correo", "detalle": f"El correo {correo} ya está registrado."}])

                for emp_data in data.get("empleados", []):
                    empleado = Empleado(
                        nombre=emp_data["nombre"],
                        apellido=emp_data["apellido"],
                        correo=emp_data["correo"],
                        cargo=emp_data["cargo"],
                        salario=emp_data["salario"],
                        compania_id=compania_creada.id,
                    )
                    # Validación de reglas de negocio en el dominio
                    empleado.validar()

                    empleado_creado = self._uow.empleado_repository.create(empleado)
                    empleados_creados.append(empleado_creado)
                    logger.info("Empleado creado en transacción: ID=%s, nombre=%s",
                                empleado_creado.id, empleado_creado.nombre_completo())

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

    def patch_compania(self, compania_id: int, data: Dict[str, Any]) -> Optional[Compania]:
        """Actualización parcial de una compañía."""
        logger.info("Patching compañía con ID: %s", compania_id)
        with self._uow:
            existing = self._uow.compania_repository.get_by_id(compania_id)
            if not existing:
                return None
            
            # Apply partial updates
            if "nombre" in data: existing.nombre = data["nombre"]
            if "direccion" in data: existing.direccion = data["direccion"]
            if "telefono" in data: existing.telefono = data["telefono"]
            
            existing.__post_init__()
            existing.validar()
            
            updated = self._uow.compania_repository.patch(compania_id, data)
            self._uow.commit()
            return updated

    def get_paginated_companias(
        self, page: int = 1, size: int = 10, sort_by: str = "", sort_dir: str = "asc", search: str = ""
    ) -> Dict[str, Any]:
        """Obtener lista paginada de compañías."""
        logger.info("Obteniendo compañías paginadas: page=%s, size=%s", page, size)
        with self._uow:
            return self._uow.compania_repository.get_paginated(
                page=page, size=size, sort_by=sort_by, sort_dir=sort_dir, search=search
            )
