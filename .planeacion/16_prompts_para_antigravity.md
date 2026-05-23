# Prompts Para Antigravity

## Prompt Arquitectura

Genera una API REST en Django aplicando Onion Architecture.

Debe incluir:
- Domain
- Application
- Infrastructure
- API

Usar:
- Django REST Framework
- Repository Pattern
- Unit Of Work con transaction.atomic
- Service Layer

No permitir acceso directo al ORM desde controllers.

---

## Prompt Repositories

Crea repositories para Compania y Empleado usando Django ORM.

Los repositories NO deben hacer commit.

---

## Prompt Unit Of Work

Implementa Unit Of Work usando transaction.atomic.

Debe permitir:
- commit
- rollback
- manejo transaccional

---

## Prompt Endpoint Transaccional

Crear endpoint:
POST /api/companias/con-empleados

Debe crear:
- una compañía
- múltiples empleados

Todo en una sola transacción.
Si falla algo:
rollback completo.