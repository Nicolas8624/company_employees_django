# Plan de implementacion para Django

Este plan esta pensado para el proyecto existente `company_employees_django`.

## Fase 0 - Diagnostico

Revisar:

- `domain/entities`
- `domain/interfaces`
- `application/services`
- `infrastructure/database/models.py`
- `infrastructure/repositories`
- `infrastructure/unit_of_work`
- `api/controllers`
- `api/serializers`
- `api/routes/urls.py`
- `tests`
- `requirements.txt`

Confirmar que el flujo siga siendo:

```text
Controller -> Service -> UnitOfWork -> Repository -> ORM -> DB
```

## Fase 1 - CRUD de colecciones

### Domain

Actualizar interfaces:

- `IEmpleadoRepository`
  - `bulk_create(empleados)`
  - `patch(empleado_id, data)`
  - `delete_many(ids)`
  - `get_paginated(filters)`

- `ICompaniaRepository`
  - si aplica: `patch`, `get_paginated`

### Infrastructure

Implementar en repositorios:

- `bulk_create`
- `patch`
- `delete_many`
- busqueda por nombre/apellido/correo
- ordenamiento seguro solo por campos permitidos
- paginacion

No hacer commit dentro del repositorio.

### Application

Agregar en servicios:

- `bulk_create_empleados`
- `patch_empleado`
- `delete_many_empleados`
- `list_empleados_paginated`

Todas las operaciones masivas deben usar `with self._uow:`.

### API

Agregar rutas:

```http
POST   /api/empleados/bulk
PATCH  /api/empleados/{id}
DELETE /api/empleados/bulk-delete
GET    /api/empleados?pagina=1&tamano=10&orden=apellido&dir=asc&buscar=gomez
```

## Fase 2 - Validaciones

Crear o mejorar DTOs/serializers:

- `EmpleadoCreateSerializer`
- `EmpleadoPatchSerializer`
- `EmpleadoBulkCreateSerializer`
- `BulkDeleteSerializer`
- `PaginationQuerySerializer`

Agregar validaciones de negocio en Application:

- correo unico.
- compania existente.
- salario positivo.

Crear excepcion de aplicacion:

- `ValidationError`
- `NotFoundError`
- `ForbiddenError`

Crear handler/middleware para formato uniforme.

## Fase 3 - Seguridad JWT

Instalar o usar:

```powershell
pip install djangorestframework-simplejwt
```

O implementar JWT con `PyJWT` si se quiere controlar mas la arquitectura.

Recomendacion para esta actividad:

- Usar `djangorestframework-simplejwt` por ser estandar en DRF.
- Mantener la logica de auth en `application/services/auth_service.py`.
- Crear wrappers/adaptadores en infrastructure si hace falta.

### Domain

Agregar:

- `domain/entities/usuario.py`
- `domain/interfaces/i_usuario_repository.py`
- `domain/interfaces/i_token_service.py`
- `domain/interfaces/i_password_hasher.py`

### Infrastructure

Agregar:

- `UsuarioModel` en `infrastructure/database/models.py`
- `UsuarioRepository`
- `JwtTokenService`
- `DjangoPasswordHasher`

### Application

Agregar:

- `AuthService`
  - `registrar`
  - `login`
  - `perfil`

### API

Agregar:

- `AuthController`
- serializers de registro/login
- permisos por rol
- middleware o permission classes

Rutas:

```http
POST /api/auth/registro
POST /api/auth/login
GET  /api/auth/perfil
```

## Fase 4 - Roles

Definir roles:

```text
ADMIN
USUARIO
```

Crear permission classes:

- `IsAuthenticatedJwt`
- `IsAdmin`
- `IsAdminOrUser`

Matriz:

| Operacion | Rol |
|---|---|
| GET | autenticado |
| POST | ADMIN o USUARIO |
| PUT/PATCH | ADMIN o USUARIO |
| DELETE | ADMIN |
| companias/con-empleados | ADMIN |

## Fase 5 - Politicas

Crear politica:

```text
EsPropietarioDeCompania
```

Implementacion sugerida:

- `api/permissions/policies.py`
- Metodo que consulte el empleado por id usando el service, no el ORM directo desde el controller.
- Permitir si:
  - usuario.rol == ADMIN
  - o usuario.compania_id == empleado.compania_id

Aplicar a:

```http
PATCH /api/empleados/{id}
DELETE /api/empleados/{id}
```

## Fase 6 - Pruebas

Agregar pruebas:

- `tests/test_collection_crud.py`
- `tests/test_validation.py`
- `tests/test_auth_jwt.py`
- `tests/test_policies.py`
- mantener o ampliar `tests/test_services.py`

Casos obligatorios:

- bulk create exitoso.
- bulk create con un empleado invalido hace rollback.
- PATCH actualiza solo campos enviados.
- delete many elimina todos los ids enviados.
- listado paginado devuelve envelope.
- login devuelve token.
- sin token responde 401.
- usuario sin rol responde 403.
- politica ownership permite/deniega correctamente.

## Fase 7 - README y evidencias

Actualizar README con:

- CRUD de colecciones.
- Async.
- Validaciones.
- Pruebas.
- Seguridad JWT.
- Roles.
- Politicas.
- Variables de entorno.
- Comparacion con ASP.NET Core.
- Conclusiones.
