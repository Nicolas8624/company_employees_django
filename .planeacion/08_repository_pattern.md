# Repository Pattern

Los repositorios deben encapsular el acceso a datos.

Métodos obligatorios:

- get_all()
- get_by_id()
- create()
- update()
- delete()
- find_by_condition()

IMPORTANTE:
Los repositorios NO hacen commit.
El commit lo maneja UnitOfWork.