"""
Excepciones del dominio.

Excepciones propias de la capa de dominio que NO dependen de Django
ni de ningún framework externo. Permiten comunicar errores de negocio
de forma desacoplada.
"""


class DomainException(Exception):
    """Excepción base del dominio."""

    def __init__(self, mensaje: str) -> None:
        self.mensaje = mensaje
        super().__init__(self.mensaje)


class DomainValidationError(DomainException):
    """
    Error de validación de reglas de negocio.

    Se lanza cuando una entidad de dominio no cumple
    con sus invariantes o reglas de negocio.
    """
    pass


class EntityNotFoundError(DomainException):
    """
    Error cuando una entidad no se encuentra.

    Se lanza cuando se busca una entidad por ID
    y no existe en el repositorio.
    """
    pass
