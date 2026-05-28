# Arquitectura objetivo

La arquitectura debe conservar Onion Architecture.

## Capas

```text
domain
  entities
  interfaces

application
  services
  dtos
  exceptions
  validators

infrastructure
  database
  repositories
  unit_of_work
  security
  seed

api
  controllers
  serializers
  permissions
  routes
  middlewares
```

## Dependencias permitidas

```text
api -> application
api -> infrastructure solo para composicion/inyeccion si el proyecto aun no tiene contenedor
application -> domain
infrastructure -> domain
infrastructure -> Django ORM
domain -> nada externo
```

## Dependencias prohibidas

```text
domain -> django
domain -> rest_framework
application -> infrastructure.database.models
application -> Django ORM
repository -> commit manual fuera del UnitOfWork
controller -> ORM directo
controller -> reglas de negocio complejas
```

## Flujo de una peticion normal

```text
HTTP Request
  -> Controller/APIView
  -> Serializer/DTO
  -> Application Service
  -> UnitOfWork
  -> Repository interface
  -> Repository implementation
  -> Django ORM
  -> SQLite
```

## Flujo con seguridad

```text
HTTP Request
  -> JWT middleware / permission class
  -> Role check
  -> Policy check si aplica
  -> Controller
  -> Service
  -> UnitOfWork
  -> Repository
  -> ORM
```

## Ubicacion de JWT

Domain:

- Entidad `Usuario`.
- Interfaces:
  - `IUsuarioRepository`
  - `ITokenService`
  - `IPasswordHasher`

Application:

- `AuthService`.
- Casos de uso:
  - registrar usuario.
  - iniciar sesion.
  - obtener perfil.

Infrastructure:

- Modelo ORM `UsuarioModel`.
- Repositorio `UsuarioRepository`.
- Servicio JWT concreto.
- Servicio hash de contrasenas.

API:

- `AuthController`.
- Serializers de auth.
- Permission classes.
- Politicas.

## Nota sobre validaciones

DRF serializers pueden validar formato de entrada HTTP, pero las reglas importantes del negocio deben quedar tambien en Application.

Ejemplos de reglas de negocio:

- correo unico.
- compania existente.
- usuario solo puede editar empleados de su compania.
- salario mayor que cero.

## Nota sobre async en Django

Django soporta vistas async, y versiones modernas tienen metodos async del ORM. Sin embargo, no toda la cadena es async de forma uniforme, especialmente con transacciones y codigo existente basado en `transaction.atomic`.

Para esta actividad se puede:

- implementar una refactorizacion parcial y documentarla, o
- justificar que se mantiene sync por seguridad transaccional y se documenta la alternativa idiomatica.

Lo importante es explicar la decision tecnica.
