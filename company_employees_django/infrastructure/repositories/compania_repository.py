"""
Implementación concreta del repositorio de Compañías.

Usa Django ORM para persistencia. NUNCA hace commit.
El commit es responsabilidad exclusiva del UnitOfWork.
"""
import logging
from typing import Any, Dict, List, Optional

from domain.entities.compania import Compania
from domain.interfaces.i_compania_repository import ICompaniaRepository
from infrastructure.database.models import CompaniaModel

logger = logging.getLogger(__name__)


class CompaniaRepository(ICompaniaRepository):
    """Repositorio concreto para compañías usando Django ORM."""

    def _to_entity(self, model: CompaniaModel) -> Compania:
        """Convertir modelo ORM a entidad de dominio."""
        return Compania(
            id=model.pk,
            nombre=model.nombre,
            direccion=model.direccion,
            telefono=model.telefono,
            fecha_creacion=model.fecha_creacion,
        )

    def get_all(self) -> List[Compania]:
        """Obtener todas las compañías."""
        models = CompaniaModel.objects.all()
        return [self._to_entity(m) for m in models]

    def get_by_id(self, compania_id: int) -> Optional[Compania]:
        """Obtener una compañía por su ID."""
        try:
            model = CompaniaModel.objects.get(pk=compania_id)
            return self._to_entity(model)
        except CompaniaModel.DoesNotExist:
            return None

    def create(self, compania: Compania) -> Compania:
        """
        Crear una nueva compañía. NO hace commit.
        El commit es responsabilidad del UnitOfWork.
        """
        model = CompaniaModel.objects.create(
            nombre=compania.nombre,
            direccion=compania.direccion,
            telefono=compania.telefono,
        )
        logger.debug("Repository: Compañía insertada (sin commit explícito) ID=%s", model.pk)
        return self._to_entity(model)

    def update(self, compania_id: int, data: Dict[str, Any]) -> Optional[Compania]:
        """
        Actualizar una compañía existente. NO hace commit.
        """
        try:
            model = CompaniaModel.objects.get(pk=compania_id)
        except CompaniaModel.DoesNotExist:
            return None

        for field, value in data.items():
            if hasattr(model, field):
                setattr(model, field, value)
        model.save()
        logger.debug("Repository: Compañía actualizada (sin commit explícito) ID=%s", model.pk)
        return self._to_entity(model)

    def delete(self, compania_id: int) -> bool:
        """
        Eliminar una compañía. NO hace commit.
        """
        try:
            model = CompaniaModel.objects.get(pk=compania_id)
            model.delete()
            logger.debug("Repository: Compañía eliminada (sin commit explícito) ID=%s", compania_id)
            return True
        except CompaniaModel.DoesNotExist:
            return False

    def find_by_condition(self, **kwargs: Any) -> List[Compania]:
        """Buscar compañías por condición."""
        models = CompaniaModel.objects.filter(**kwargs)
        return [self._to_entity(m) for m in models]
