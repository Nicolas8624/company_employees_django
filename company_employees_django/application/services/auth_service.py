"""
Servicio de Aplicación para Autenticación.
"""
import logging
from typing import Dict

from domain.entities.usuario import Usuario
from domain.exceptions import DomainValidationError, EntityNotFoundError
from domain.interfaces.i_password_hasher import IPasswordHasher
from domain.interfaces.i_token_service import ITokenService
from domain.interfaces.i_unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class AuthService:
    """Orquestador para operaciones de autenticación."""

    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ) -> None:
        self._uow = unit_of_work
        self._hasher = password_hasher
        self._token_service = token_service

    def registro(self, data: Dict) -> dict:
        """
        Registra un nuevo usuario y devuelve un token.
        
        data: {"correo": str, "password": str, "rol": str, "compania_id": int}
        """
        logger.info("Iniciando registro para correo: %s", data.get("correo"))
        
        with self._uow:
            # Validar unicidad del correo
            if self._uow.usuario_repository.find_by_correo(data.get("correo")):
                raise DomainValidationError("Error de validacion", errores=[{"campo": "correo", "detalle": "El correo ya está registrado."}])

            # Validar compania si el rol es USUARIO
            rol = data.get("rol", "USUARIO").upper()
            compania_id = data.get("compania_id")

            if rol == "USUARIO" and not compania_id:
                raise DomainValidationError("Error de validacion", errores=[{"campo": "compania_id", "detalle": "Un USUARIO debe pertenecer a una compañía."}])

            if compania_id:
                if not self._uow.compania_repository.get_by_id(compania_id):
                    raise DomainValidationError("Error de validacion", errores=[{"campo": "compania_id", "detalle": "La compañía indicada no existe."}])

            usuario = Usuario(
                correo=data.get("correo"),
                password_hash=self._hasher.hash_password(data.get("password")),
                rol=rol,
                compania_id=compania_id
            )
            usuario.validar()

            creado = self._uow.usuario_repository.create(usuario)
            self._uow.commit()

        token = self._token_service.generate_token(creado)
        return {
            "usuario": {
                "id": creado.id,
                "correo": creado.correo,
                "rol": creado.rol,
                "compania_id": creado.compania_id
            },
            "token": token
        }

    def login(self, correo: str, password: str) -> dict:
        """
        Verifica credenciales y devuelve un token.
        """
        logger.info("Iniciando login para correo: %s", correo)
        
        usuario = self._uow.usuario_repository.find_by_correo(correo)
        if not usuario:
            raise DomainValidationError("Error de autenticación", errores=[{"campo": "credenciales", "detalle": "Credenciales inválidas."}])

        if not self._hasher.verify_password(password, usuario.password_hash):
            raise DomainValidationError("Error de autenticación", errores=[{"campo": "credenciales", "detalle": "Credenciales inválidas."}])

        token = self._token_service.generate_token(usuario)
        return {
            "usuario": {
                "id": usuario.id,
                "correo": usuario.correo,
                "rol": usuario.rol,
                "compania_id": usuario.compania_id
            },
            "token": token
        }
