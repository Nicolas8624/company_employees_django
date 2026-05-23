# infrastructure/repositories/__init__.py
from infrastructure.repositories.compania_repository import CompaniaRepository
from infrastructure.repositories.empleado_repository import EmpleadoRepository

__all__ = ["CompaniaRepository", "EmpleadoRepository"]
