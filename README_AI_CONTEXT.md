# README_AI_CONTEXT.md

## Contexto General del Proyecto

Este proyecto es una actividad académica enfocada en transferir conceptos de ASP.NET Core Web API hacia otro ecosistema tecnológico utilizando Python con Django.

El proyecto debe implementar una API REST completa aplicando Onion Architecture, Repository Pattern y Unit Of Work.

La solución debe demostrar separación de responsabilidades, manejo correcto de transacciones, arquitectura limpia y buenas prácticas de desarrollo backend empresarial.

---

# Objetivo Principal

Construir una API REST funcional para administrar compañías y empleados utilizando:

- Python
- Django
- Django REST Framework
- Django ORM
- Onion Architecture
- Repository Pattern
- Unit Of Work
- Service Layer
- Logging
- Migraciones
- Transacciones

---

# Arquitectura Obligatoria

El proyecto debe seguir Onion Architecture estrictamente.

## Capas requeridas

### Domain
Contiene:
- entidades
- interfaces
- reglas de dominio

NO debe depender de Django ni del ORM.

---

### Application
Contiene:
- services
- casos de uso
- DTOs
- validaciones

Debe depender únicamente de Domain.

---

### Infrastructure
Contiene:
- implementación de repositories
- configuración ORM
- base de datos
- Unit Of Work
- migraciones
- seed data

Aquí vive Django ORM.

---

### API
Contiene:
- controllers
- routes
- serializers
- middlewares
- manejo de errores
- logging

---

# Flujo Obligatorio

El proyecto DEBE respetar este flujo:

Controller
→ Service
→ UnitOfWork
→ Repository
→ ORM
→ Database

NO se permite:
- controllers usando ORM directamente
- lógica de negocio en controllers
- repositories haciendo commit

---

# Tecnologías

## Lenguaje
Python 3.12+

## Framework
Django

## API REST
Django REST Framework

## ORM
Django ORM

## Base de datos
SQLite (preferiblemente)

## Manejo transaccional
transaction.atomic

## Logging
logging de Python

---

# Reglas Técnicas

## Repository Pattern

Los repositories deben:

- encapsular acceso a datos
- manejar queries
- abstraer persistencia

Métodos esperados:
- get_all
- get_by_id
- create
- update
- delete
- find_by_condition

IMPORTANTE:
Los repositories NO deben hacer commit.

---

# Unit Of Work

El proyecto debe implementar Unit Of Work usando:

from django.db import transaction

Objetivos:
- coordinar múltiples repositories
- compartir misma transacción
- manejar commit global
- manejar rollback

Si ocurre un error:
- rollback automático
- no guardar cambios parciales

---

# Entidades

## Compania

Campos mínimos:
- id
- nombre
- direccion
- telefono
- fecha_creacion

---

## Empleado

Campos mínimos:
- id
- nombre
- apellido
- correo
- cargo
- salario
- compania_id

---

# Relación

Una compañía tiene muchos empleados.

Compania 1:N Empleado

---

# Endpoints Obligatorios

## Compañías

GET /api/companias
GET /api/companias/{id}
POST /api/companias
PUT /api/companias/{id}
DELETE /api/companias/{id}
GET /api/companias/{id}/empleados

---

## Empleados

GET /api/empleados
GET /api/empleados/{id}
POST /api/empleados
PUT /api/empleados/{id}
DELETE /api/empleados/{id}

---

# Endpoint Transaccional Obligatorio

POST /api/companias/con-empleados

Debe:
- crear una compañía
- crear múltiples empleados
- usar una sola transacción

Condición:
si falla un empleado:
- rollback completo
- no guardar nada

---

# Logging Obligatorio

Registrar:
- inicio aplicación
- creación compañía
- creación empleado
- inicio transacción
- commit
- rollback
- errores de base de datos
- errores inesperados

---

# Estructura Recomendada

project/
│
├── domain/
│   ├── entities/
│   └── interfaces/
│
├── application/
│   ├── services/
│   ├── dtos/
│   └── use_cases/
│
├── infrastructure/
│   ├── database/
│   ├── repositories/
│   ├── unit_of_work/
│   └── seed/
│
├── api/
│   ├── controllers/
│   ├── routes/
│   ├── serializers/
│   └── middlewares/
│
└── manage.py

---

# Buenas Prácticas Esperadas

- usar tipado Python
- mantener separación de capas
- usar nombres claros
- evitar duplicación
- mantener código modular
- usar principios SOLID
- usar manejo de errores global
- usar serializers correctamente
- validar datos de entrada

---

# Objetivo Académico

El proyecto debe demostrar:

- transferencia de conceptos desde ASP.NET Core
- entendimiento de Onion Architecture
- uso correcto de Repository Pattern
- uso correcto de Unit Of Work
- manejo de transacciones
- separación de responsabilidades
- diseño backend empresarial

---

# Restricciones Importantes

NO hacer:
- ORM directamente en controllers
- lógica de negocio en views
- commit dentro de repositories
- dependencias incorrectas entre capas
- acoplamiento fuerte entre módulos

---

# Resultado Esperado

Una API REST limpia, modular, mantenible y alineada con arquitectura empresarial moderna.