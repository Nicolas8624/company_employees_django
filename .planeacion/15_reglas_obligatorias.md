# Reglas Obligatorias

PROHIBIDO:
- Controllers accediendo directamente al ORM
- Repositories haciendo commit

OBLIGATORIO:
Controller
→ Service
→ UnitOfWork
→ Repository
→ ORM
→ Database
