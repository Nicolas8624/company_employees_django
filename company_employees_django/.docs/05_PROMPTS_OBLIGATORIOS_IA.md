# Prompts obligatorios de IA adaptados al proyecto Django

Guarda estos prompts y las respuestas de Antigravity como evidencia de uso de IA.

## Prompt 7 - CRUD de colecciones

Tengo una API REST en Python con Django y Django REST Framework, usando Django ORM, Onion Architecture, Repository Pattern y Unit of Work. Ya existe CRUD individual para Compania y Empleado.

Explicame e implementa como agregar operaciones sobre colecciones: creacion masiva de empleados, actualizacion parcial con PATCH, eliminacion multiple y listado con paginacion, filtrado y ordenamiento. Respeta las capas `domain`, `application`, `infrastructure` y `api`, y no permitas que el repositorio confirme transacciones.

## Prompt 8 - Programacion asincrona

En Python con Django y Django ORM, el manejo de peticiones y acceso a datos es sincrono o asincrono? Explicame que soporte real ofrece Django para vistas async y ORM async. Si conviene refactorizar, muestra como adaptar un servicio, repositorio y Unit of Work. Si no conviene para este proyecto, redacta una justificacion tecnica clara para el README.

## Prompt 9 - Validaciones

Cual es el mecanismo de validacion recomendado para Django REST Framework? Implementa validaciones para DTOs o serializers de Compania y Empleado: campos obligatorios, longitud, formato de correo, salario positivo, correo unico y existencia de compania. Devuelve errores con formato uniforme y codigo HTTP correcto, manteniendo las reglas de negocio en la capa Application.

## Prompt 10 - Pruebas

Cual es el framework de pruebas mas usado en Django y DRF? Implementa pruebas unitarias para servicios y repositorios, y pruebas de integracion para endpoints de Compania y Empleado. Incluye una prueba obligatoria que verifique rollback cuando falla la creacion masiva o la creacion transaccional de una compania con empleados.

## Prompt 11 - JWT por roles

Explicame e implementa autenticacion con JWT en Django REST Framework para este proyecto Onion: entidad Usuario, registro, login que devuelve token y proteccion de endpoints por roles ADMIN y USUARIO. Indica libreria recomendada, donde ubicar cada clase en la arquitectura, y evita guardar contrasenas en texto plano o claves JWT quemadas en el codigo.

## Prompt 12 - JWT por politicas

Cual es la diferencia entre autorizacion por roles y por politicas en Django REST Framework? Implementa una politica de propiedad: un usuario solo puede editar o eliminar empleados de su propia compania, mientras ADMIN puede todo. Comparala con las policies de ASP.NET Core usando `[Authorize(Policy="...")]`, requirements y handlers.

## Prompts adicionales recomendados

### Revision de arquitectura

Revisa si los cambios que acabas de hacer mantienen Onion Architecture. Verifica que `domain` no importe Django, que `application` no use ORM directamente, que los controllers no accedan a modelos y que Unit of Work siga controlando transacciones.

### README

Actualiza el README con las secciones exigidas por la guia: CRUD de colecciones, programacion asincrona, validaciones, pruebas, seguridad JWT, roles, politicas, variables de entorno, comparacion con ASP.NET Core y conclusiones.

### Sustentacion

Genera una explicacion corta para sustentar el proyecto Parte II, incluyendo flujo por capas, rollback, JWT, roles y politica de propiedad.
