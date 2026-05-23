# Contexto General

Proyecto académico basado en Onion Architecture usando Python + Django.

Objetivo:
Construir una API REST aplicando:

- Onion Architecture
- Repository Pattern
- Unit of Work
- Service Layer
- Django ORM
- Transacciones con atomic
- Logging
- Migraciones
- Endpoints REST

Tecnologías principales:

- Python 3.12+
- Django
- Django REST Framework
- SQLite o PostgreSQL
- Logging nativo de Python

Regla principal:
El controlador NO puede acceder directamente al ORM.
Debe existir el flujo:

Controller
→ Service
→ UnitOfWork
→ Repository
→ ORM
→ Database