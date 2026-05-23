# Unit Of Work

En Django se implementará usando:

transaction.atomic

Objetivos:

- Compartir una sola transacción
- Coordinar múltiples repositorios
- Hacer commit global
- Hacer rollback automático

Flujo:

Service
→ UnitOfWork
→ Repositories
→ ORM
→ Database