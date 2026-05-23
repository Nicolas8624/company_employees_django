# AGENTS.md

## Arquitectura obligatoria

Este proyecto debe seguir Onion Architecture estrictamente.

Capas obligatorias:

- Domain
- Application
- Infrastructure
- API

## Flujo obligatorio

Controller
→ Service
→ UnitOfWork
→ Repository
→ ORM
→ Database

## Reglas técnicas

- Los controllers NO pueden acceder directamente al ORM.
- Toda lógica de negocio debe vivir en services.
- Los repositories solo manejan persistencia.
- Los repositories NO hacen commit.
- UnitOfWork es responsable de commit y rollback.
- Usar transaction.atomic para transacciones.
- Mantener separación estricta entre capas.
- Usar tipado Python cuando sea posible.
- Mantener código limpio y modular.
- No duplicar lógica.
- Las dependencias deben apuntar hacia el dominio.

## ORM

Usar Django ORM.

## Framework

Usar Django REST Framework.

## Base de datos

Preferiblemente SQLite para simplicidad académica.

## Endpoints requeridos

### Compañías

- GET /api/companias
- GET /api/companias/{id}
- POST /api/companias
- PUT /api/companias/{id}
- DELETE /api/companias/{id}

### Empleados

- GET /api/empleados
- GET /api/empleados/{id}
- POST /api/empleados
- PUT /api/empleados/{id}
- DELETE /api/empleados/{id}

## Endpoint transaccional obligatorio

POST /api/companias/con-empleados

Debe crear:
- compañía
- múltiples empleados

Todo en una sola transacción.

Si falla algo:
rollback completo.

## Logging obligatorio

Registrar:
- inicio aplicación
- creación compañía
- creación empleado
- inicio transacción
- commit
- rollback
- errores

## Restricciones importantes

NO usar:
- lógica de negocio en controllers
- queries SQL directas innecesarias
- commit dentro de repositories
- acceso cruzado incorrecto entre capas

## Objetivo

Demostrar:
- Onion Architecture
- Repository Pattern
- Unit Of Work
- Service Layer
- Transacciones
- Logging
- Buenas prácticas REST