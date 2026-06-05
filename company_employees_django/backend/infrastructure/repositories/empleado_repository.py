"""
Implementación concreta del repositorio de Empleados.

Usa Django ORM para persistencia. NUNCA hace commit.
El commit es responsabilidad exclusiva del UnitOfWork.
"""
import logging
from typing import Any, Dict, List, Optional

from domain.entities.empleado import Empleado
from domain.interfaces.i_empleado_repository import IEmpleadoRepository
from infrastructure.database.models import EmpleadoModel

logger = logging.getLogger(__name__)


class EmpleadoRepository(IEmpleadoRepository):
    """Repositorio concreto para empleados usando Django ORM."""

    def _to_entity(self, model: EmpleadoModel) -> Empleado:
        """Convertir modelo ORM a entidad de dominio."""
        return Empleado(
            id=model.pk,
            nombre=model.nombre,
            apellido=model.apellido,
            correo=model.correo,
            cargo=model.cargo,
            salario=model.salario,
            compania_id=model.compania_id,
        )

    def get_all(self) -> List[Empleado]:
        """Obtener todos los empleados."""
        models = EmpleadoModel.objects.all()
        return [self._to_entity(m) for m in models]

    def get_by_id(self, empleado_id: int) -> Optional[Empleado]:
        """Obtener un empleado por su ID."""
        try:
            model = EmpleadoModel.objects.get(pk=empleado_id)
            return self._to_entity(model)
        except EmpleadoModel.DoesNotExist:
            return None

    def create(self, empleado: Empleado) -> Empleado:
        """
        Crear un nuevo empleado. NO hace commit.
        El commit es responsabilidad del UnitOfWork.
        """
        model = EmpleadoModel.objects.create(
            nombre=empleado.nombre,
            apellido=empleado.apellido,
            correo=empleado.correo,
            cargo=empleado.cargo,
            salario=empleado.salario,
            compania_id=empleado.compania_id,
        )
        logger.debug("Repository: Empleado insertado (sin commit explícito) ID=%s", model.pk)
        return self._to_entity(model)

    def update(self, empleado_id: int, data: Dict[str, Any]) -> Optional[Empleado]:
        """
        Actualizar un empleado existente. NO hace commit.
        """
        try:
            model = EmpleadoModel.objects.get(pk=empleado_id)
        except EmpleadoModel.DoesNotExist:
            return None

        for field, value in data.items():
            if field == "compania_id":
                model.compania_id = value
            elif hasattr(model, field):
                setattr(model, field, value)
        model.save()
        logger.debug("Repository: Empleado actualizado (sin commit explícito) ID=%s", model.pk)
        return self._to_entity(model)

    def delete(self, empleado_id: int) -> bool:
        """
        Eliminar un empleado. NO hace commit.
        """
        try:
            model = EmpleadoModel.objects.get(pk=empleado_id)
            model.delete()
            logger.debug("Repository: Empleado eliminado (sin commit explícito) ID=%s", empleado_id)
            return True
        except EmpleadoModel.DoesNotExist:
            return False

    def find_by_condition(self, **kwargs: Any) -> List[Empleado]:
        """Buscar empleados por condición."""
        models = EmpleadoModel.objects.filter(**kwargs)
        return [self._to_entity(m) for m in models]

    def get_by_compania(self, compania_id: int) -> List[Empleado]:
        """Obtener todos los empleados de una compañía."""
        models = EmpleadoModel.objects.filter(compania_id=compania_id)
        return [self._to_entity(m) for m in models]

    def bulk_create(self, empleados: List[Empleado]) -> List[Empleado]:
        """Crear múltiples empleados. NO hace commit."""
        models = [
            EmpleadoModel(
                nombre=e.nombre,
                apellido=e.apellido,
                correo=e.correo,
                cargo=e.cargo,
                salario=e.salario,
                compania_id=e.compania_id
            ) for e in empleados
        ]
        created_models = EmpleadoModel.objects.bulk_create(models)
        logger.debug("Repository: %s Empleados insertados en bulk (sin commit explícito)", len(created_models))
        # Si la base de datos no devuelve PKs en bulk_create (como SQLite antiguo), 
        # las entidades devueltas podrían no tener ID.
        return [self._to_entity(m) for m in created_models]

    def patch(self, empleado_id: int, data: Dict[str, Any]) -> Optional[Empleado]:
        """Actualizar parcialmente un empleado existente. NO hace commit."""
        return self.update(empleado_id, data)

    def delete_many(self, ids: List[int]) -> int:
        """Eliminar múltiples empleados. NO hace commit."""
        count, _ = EmpleadoModel.objects.filter(pk__in=ids).delete()
        logger.debug("Repository: %s Empleados eliminados en bulk (sin commit explícito)", count)
        return count

    def get_paginated(self, page: int, size: int, sort_by: str, sort_dir: str, search: str) -> Dict[str, Any]:
        """Obtener empleados paginados con ordenamiento y búsqueda."""
        from django.db.models import Q
        import math
        
        qs = EmpleadoModel.objects.all()
        
        if search:
            qs = qs.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(correo__icontains=search) |
                Q(cargo__icontains=search)
            )
            
        if sort_by:
            prefix = "-" if sort_dir.lower() == "desc" else ""
            valid_fields = ["id", "nombre", "apellido", "correo", "cargo", "salario"]
            if sort_by in valid_fields:
                qs = qs.order_by(f"{prefix}{sort_by}")
                
        total = qs.count()
        start = (page - 1) * size
        end = start + size
        
        models = qs[start:end]
        total_paginas = math.ceil(total / size) if size > 0 else 0
        
        return {
            "datos": [self._to_entity(m) for m in models],
            "pagina": page,
            "tamano": size,
            "total": total,
            "total_paginas": total_paginas
        }
