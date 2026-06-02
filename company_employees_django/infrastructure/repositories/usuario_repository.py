"""
Implementación del repositorio de Usuarios usando Django ORM.

Al igual que los otros repositorios, NO hace commit explícito.
"""
import logging
from typing import Optional

from domain.entities.usuario import Usuario
from domain.interfaces.i_usuario_repository import IUsuarioRepository
from infrastructure.database.models import UsuarioModel

logger = logging.getLogger(__name__)


class UsuarioRepository(IUsuarioRepository):
    """Implementación concreta de IUsuarioRepository."""

    def _to_entity(self, model: UsuarioModel) -> Usuario:
        """Mapear modelo ORM a Entidad de Dominio."""
        return Usuario(
            id=model.id,
            correo=model.correo,
            password_hash=model.password_hash,
            rol=model.rol,
            ciudad=model.ciudad,
            compania_id=model.compania_id,
        )

    def get_by_id(self, entity_id: int) -> Optional[Usuario]:
        try:
            model = UsuarioModel.objects.get(pk=entity_id)
            return self._to_entity(model)
        except UsuarioModel.DoesNotExist:
            return None

    def get_all(self) -> list[Usuario]:
        models = UsuarioModel.objects.all()
        return [self._to_entity(m) for m in models]

    def create(self, entity: Usuario) -> Usuario:
        model = UsuarioModel.objects.create(
            correo=entity.correo,
            password_hash=entity.password_hash,
            rol=entity.rol,
            ciudad=entity.ciudad,
            compania_id=entity.compania_id,
        )
        logger.debug("Repository: Usuario insertado (sin commit) ID=%s", model.id)
        return self._to_entity(model)

    def update(self, entity_id: int, entity_data: dict) -> Optional[Usuario]:
        try:
            model = UsuarioModel.objects.get(pk=entity_id)
            for key, value in entity_data.items():
                setattr(model, key, value)
            model.save()
            logger.debug("Repository: Usuario actualizado (sin commit) ID=%s", model.id)
            return self._to_entity(model)
        except UsuarioModel.DoesNotExist:
            return None

    def delete(self, entity_id: int) -> bool:
        try:
            model = UsuarioModel.objects.get(pk=entity_id)
            model.delete()
            logger.debug("Repository: Usuario eliminado (sin commit) ID=%s", entity_id)
            return True
        except UsuarioModel.DoesNotExist:
            return False

    def find_by_correo(self, correo: str) -> Optional[Usuario]:
        try:
            model = UsuarioModel.objects.get(correo=correo)
            return self._to_entity(model)
        except UsuarioModel.DoesNotExist:
            return None
