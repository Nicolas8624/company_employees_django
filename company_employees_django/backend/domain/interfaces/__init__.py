# domain/interfaces/__init__.py
from domain.interfaces.i_compania_repository import ICompaniaRepository
from domain.interfaces.i_empleado_repository import IEmpleadoRepository
from domain.interfaces.i_unit_of_work import IUnitOfWork

__all__ = ["ICompaniaRepository", "IEmpleadoRepository", "IUnitOfWork"]
