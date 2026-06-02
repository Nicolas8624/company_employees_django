# 📘 Manual de Implementación y Evidencias — Parte II
Este manual documenta en detalle todas las funcionalidades implementadas en la **Parte II** del proyecto, siguiendo estrictamente la **Onion Architecture** y respondiendo de forma clara y técnica a la guía y prompts de IA establecidos por el SENA.

---

## 🧅 Resumen de Flujo en Onion Architecture
El flujo de control de todas las peticiones mantiene una separación rigurosa entre las capas, con las dependencias apuntando siempre hacia el núcleo de dominio:

```mermaid
graph TD
    Client[Cliente HTTP] -->|Petición| Controller[API Controller Capa API]
    Controller -->|Valida DTO/Estructura| Serializer[DRF Serializers Capa API]
    Controller -->|Llama Caso de Uso| Service[Application Service Capa Application]
    Service -->|Inicia Transacción / Controla| UoW[Unit of Work Capa Infrastructure]
    Service -->|Lee/Escribe a través de Interfaces| Repository[Repository Capa Infrastructure]
    Repository -->|Consulta| ORM[Django ORM Capa Infrastructure]
    ORM -->|Persiste| DB[(Base de Datos SQLite)]
```

---

## 1. CRUD de Colecciones y Operaciones Masivas (Módulo 1)

### Endpoints Implementados
*   **Creación Masiva:** `POST /api/empleados/bulk`
*   **Actualización Parcial:** `PATCH /api/empleados/{id}`
*   **Eliminación Múltiple:** `DELETE /api/empleados/bulk-delete`
*   **Listado Avanzado:** `GET /api/empleados?pagina=1&tamano=10&orden=apellido&dir=asc&buscar=gomez`

### Explicación Técnica de Funcionamiento

#### A. Cómo funciona el Bulk Insert
La creación masiva recibe una lista de empleados en formato JSON. El controlador delega al servicio `EmpleadoService.bulk_create_empleados()`. Éste, dentro de un bloque controlado por el `UnitOfWork`, mapea los DTOs a entidades de dominio y las pasa a `EmpleadoRepository.bulk_create()`. 
El repositorio utiliza el método `bulk_create` del Django ORM, lo que realiza **una sola sentencia SQL `INSERT` optimizada** para insertar todos los registros de golpe, mejorando exponencialmente el rendimiento en comparación con inserciones individuales en bucle.

#### B. Garantía Transaccional con Unit of Work (UoW)
Tanto la creación masiva como el endpoint transaccional de creación de compañías con empleados utilizan el patrón **Unit of Work** (`UnitOfWork`).
*   El `UnitOfWork` gestiona el contexto transaccional mediante `transaction.atomic()` de Django.
*   Los repositorios **no hacen commit ni rollback**. Simplemente operan sobre la sesión del ORM.
*   Si todas las operaciones en el servicio terminan con éxito, el servicio marca la transacción como exitosa llamando a `uow.commit()`.
*   Si ocurre cualquier excepción de dominio (`DomainValidationError`) o de base de datos (`IntegrityError`), el bloque contextual se encarga de revertir automáticamente todas las operaciones con un `rollback()`.

#### C. Cómo funciona el PATCH (Actualización Parcial)
El método `PATCH` permite actualizar únicamente los campos provistos en el cuerpo del request (por ejemplo, solo modificar el `salario` y `cargo` sin tener que enviar nombre, apellido, correo, etc.).
1. El controlador recibe el payload y lo valida con `EmpleadoPatchSerializer(partial=True)`.
2. Se recupera el empleado existente de la base de datos por su ID para verificar su existencia y aplicar las reglas de propiedad del objeto.
3. El servicio `EmpleadoService.patch_empleado()` toma la entidad existente, reemplaza solo los campos que vienen en el payload, ejecuta las validaciones de negocio correspondientes, y delega al repositorio para persistir la entidad modificada en la base de datos.

#### D. Cómo funciona la Eliminación Múltiple (Bulk Delete)
El endpoint `DELETE /api/empleados/bulk-delete` recibe una lista de IDs `{"ids": [1, 2, 3]}`.
1. El controlador valida el cuerpo usando `BulkDeleteSerializer`.
2. El servicio delega al repositorio `EmpleadoRepository.delete_many(ids)`.
3. El repositorio ejecuta una sentencia SQL eficiente equivalent a `DELETE FROM empleados WHERE id IN (1, 2, 3)` usando `EmpleadoModel.objects.filter(id__in=ids).delete()`. Esto asegura una eliminación masiva de registros en un solo paso de I/O de base de datos.

#### E. Paginación, Filtrado y Ordenación
El listado `GET /api/empleados` permite administrar grandes volúmenes de datos mediante parámetros dinámicos en la URL:
*   `pagina` y `tamano`: Definen la fracción de datos a mostrar. El servicio calcula el offset (`(pagina - 1) * tamano`) y limita la consulta del ORM usando slicing `[offset:offset+tamano]`.
*   `orden` y `dir`: Definen el campo de ordenamiento (ej. `salario`, `nombre`) y el sentido (`asc` o `desc`). El repositorio traduce esto a un formato que Django ORM comprende (ej. `order_by('-salario')` para descendente).
*   `buscar`: Realiza una búsqueda insensible a mayúsculas y minúsculas (filtro `icontains` en múltiples campos como `nombre`, `apellido` o `correo`).

---

## 2. Programación Asíncrona (Módulo 2)

### Justificación Técnica de la Decisión
Se determinó **mantener el modelo sincrónico** para este stack en particular. A continuación se detallan las razones arquitectónicas de esta decisión:

1.  **Integridad del Unit of Work y Transaccionalidad:** Django ORM es inherentemente sincrónico. Aunque existen versiones recientes que soportan consultas asíncronas (`abase()`, `aatomic()`), el soporte de transacciones asíncronas seguras en patrones complejos como Unit of Work y repositorios aún no es lo suficientemente maduro ni estable en el ecosistema Django REST Framework, lo que incrementa el riesgo de pérdidas de contexto transaccional o deadlocks.
2.  **Base de Datos SQLite:** El motor SQLite maneja de forma ineficiente las transacciones simultáneas asíncronas debido a su bloqueo a nivel de archivo completo (bloqueo de base de datos al escribir). Introducir operaciones asíncronas no mejoraría la concurrencia en SQLite; al contrario, generaría excepciones frecuentes de tipo `database is locked`.
3.  **Desacoplamiento y Onion Architecture:** Introducir `async/await` a lo largo de toda la aplicación obligaría a definir todas las interfaces de los repositorios y servicios como asíncronas. Esto complicaría la legibilidad y mantenimiento del código sin otorgar un beneficio real en el rendimiento de I/O de red, ya que el backend corre de forma local y los procesos son rápidos.

---

## 3. Validaciones Globales y Manejo de Errores (Módulo 3)

### Mecanismo de Validación
*   **Capa API (Serializers):** Validan la estructura de datos entrantes, tipos (ej. que un correo tenga formato de correo, o que un salario sea un número) y longitudes máximas.
*   **Capa Application (Services):** Ejecutan las **reglas de negocio duras** antes de proceder con el guardado en base de datos. Las reglas validadas en el servicio incluyen:
    *   **Salario Positivo:** El salario debe ser mayor a cero.
    *   **Correo Único:** Ningún empleado puede registrarse con un correo que ya exista en la base de datos.
    *   **Compañía Existente:** No se puede crear un empleado en una compañía que no existe en el sistema.

### Middleware Global de Errores
Se implementó `ErrorHandlerMiddleware` en `api/middlewares/error_handler.py`. Captura todas las excepciones que no sean manejadas en los controladores (como `DomainValidationError`, `EntityNotFoundError`, etc.) y las devuelve en un formato estructurado con el código HTTP apropiado:

```json
{
  "mensaje": "Error de validacion",
  "errores": [
    {
      "campo": "correo",
      "detalle": "El correo ya se encuentra registrado."
    }
  ]
}
```

---

## 4. Seguridad JWT, Roles y Políticas (Módulos 4 & 5)

Se implementó autenticación con **JSON Web Tokens (JWT)**, autorización por **roles** (`ADMIN` / `USUARIO`) y dos **políticas** basadas en claims del token: propiedad de compañía y ciudad del administrador.

### 4.1 Flujo técnico (Onion Architecture)

```
[Cliente HTTP]
    |  Authorization: Bearer <JWT>
    v
[JwtCustomAuthentication]          ← infrastructure/security/jwt_authentication.py
    |  Valida firma (djangorestframework-simplejwt)
    |  Lee claims: user_id, correo, rol, ciudad, compania_id
    |  Crea UsuarioAutenticado → request.user
    v
[Permission classes]               ← api/permissions/permissions.py
    |  Rol: IsAdmin, IsAdminOrUsuario, IsAuthenticatedUser
    |  Políticas: EsPropietarioDeCompania, PoliticaAdminCiudad
    v
[Controller] → [Service] → [UnitOfWork] → [Repository] → ORM
```

| Capa | Archivos principales | Responsabilidad |
|------|----------------------|-----------------|
| **Domain** | `domain/entities/usuario.py`, `domain/interfaces/i_token_service.py` | Entidad `Usuario`, contratos sin dependencias web |
| **Application** | `application/services/auth_service.py` | Registro, login, validación de credenciales |
| **Infrastructure** | `infrastructure/security/token_service.py`, `jwt_authentication.py`, `password_hasher.py`, `infrastructure/repositories/usuario_repository.py` | JWT, hash de contraseñas, persistencia |
| **API** | `api/controllers/auth_controller.py`, `api/permissions/permissions.py` | Endpoints HTTP y reglas de acceso |

### 4.2 Endpoints de autenticación

| Método | Ruta | Acceso | Descripción |
|--------|------|--------|-------------|
| `POST` | `/api/auth/registro` | Público | Crea usuario y devuelve token |
| `POST` | `/api/auth/login` | Público | Valida credenciales y devuelve token |
| `GET` | `/api/auth/perfil` | Autenticado | Devuelve datos del usuario desde el JWT |

#### Login (ejemplo)

**Request:**

```http
POST /api/auth/login
Content-Type: application/json

{
  "correo": "admin_bogota@sena.edu.co",
  "password": "Admin123!"
}
```

**Response (200):**

```json
{
  "usuario": {
    "id": 3,
    "correo": "admin_bogota@sena.edu.co",
    "rol": "ADMIN",
    "ciudad": "Bogotá",
    "compania_id": null
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Uso del token en peticiones protegidas:**

```http
GET /api/empleados
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Registro (ejemplo ADMIN con ciudad)

```json
{
  "correo": "nuevo.admin@empresa.com",
  "password": "Pass123!",
  "rol": "ADMIN",
  "ciudad": "Medellín"
}
```

Para rol `USUARIO` es obligatorio enviar `compania_id`.

### 4.3 Claims del JWT

Al iniciar sesión, `JwtTokenService` incluye en el access token:

| Claim | Descripción |
|-------|-------------|
| `user_id` | ID del usuario en base de datos |
| `correo` | Correo electrónico |
| `rol` | `ADMIN` o `USUARIO` |
| `ciudad` | Ciudad del usuario (política de administrador) |
| `compania_id` | ID de compañía (solo si aplica) |
| `exp` | Expiración (configurada en `SIMPLE_JWT` en `config/settings.py`) |

El backend `JwtCustomAuthentication` mapea esos claims a `request.user` (`UsuarioAutenticado`) sin usar `django.contrib.auth.User`.

### 4.4 Autorización por roles

| Operación HTTP | Endpoints típicos | Permiso |
|----------------|-------------------|---------|
| `GET` (listar / detalle) | `/api/companias`, `/api/empleados`, … | `IsAuthenticatedUser` |
| `POST`, `PUT`, `PATCH` | Crear / actualizar recursos | `IsAdminOrUsuario` |
| `DELETE` | Eliminar recurso o bulk-delete | `IsAdmin` |
| `POST` transaccional | `/api/companias/con-empleados` | `IsAdmin` |

**Reglas por rol:**

- **`ADMIN`:** Puede crear, leer, actualizar y (según ciudad) eliminar.
- **`USUARIO`:** Puede leer todo lo autenticado; puede crear/actualizar empleados con restricción de compañía; **no** puede `DELETE` ni usar el endpoint transaccional de compañía con empleados.

### 4.5 Políticas (Módulo 5)

Las políticas se combinan con los permisos de rol en los controllers (`get_permissions()`).

#### Política 1: `EsPropietarioDeCompania`

**Archivo:** `api/permissions/permissions.py`

| Rol | Comportamiento |
|-----|----------------|
| `ADMIN` | Sin restricción por compañía |
| `USUARIO` | Solo `PUT` / `PATCH` sobre empleados cuyo `compania_id` coincide con el del token |

Se valida en `has_object_permission()` comparando `request.user.compania_id` con `empleado.compania_id`.

#### Política 2: `PoliticaAdminCiudad` (claims + ciudad)

**Requisito de negocio:** el claim `ciudad` del JWT define qué puede hacer un **ADMIN**.

| Ciudad (claim) | Permisos del ADMIN |
|----------------|-------------------|
| **Medellín** | CRUD completo: `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **Bogotá** | Todo **excepto eliminar**: `GET`, `POST`, `PUT`, `PATCH` — `DELETE` → **403 Forbidden** |

La comparación de ciudad **ignora tildes y mayúsculas** (`Bogotá`, `bogota`, `BOGOTA` se tratan igual).

**Mensaje de error (403):**

```text
Acceso restringido: los administradores de Bogotá no pueden eliminar recursos (operación DELETE no permitida).
```

**Endpoints donde aplica `PoliticaAdminCiudad`:**

- `DELETE` en `/api/companias/{id}` y `/api/empleados/{id}`
- `DELETE` en `/api/empleados/bulk-delete`
- Cualquier ruta que use `PoliticaAdminCiudad` junto con permisos de escritura (la política solo bloquea `DELETE` para ADMIN de Bogotá)

### 4.6 Matriz resumida de acceso

| Usuario | GET | POST / PUT / PATCH | DELETE |
|---------|-----|-------------------|--------|
| Sin token | 401 | 401 | 401 |
| USUARIO (propia compañía en empleados) | Sí | Sí (empleados de su compañía) | No |
| USUARIO (otra compañía) | Sí | No (403) en empleados ajenos | No |
| ADMIN Medellín | Sí | Sí | Sí |
| ADMIN Bogotá | Sí | Sí | **No (403)** |

### 4.7 Usuarios de prueba (seed)

Ejecutar:

```powershell
py manage.py migrate
py manage.py seed
```

| Correo | Contraseña | Rol | Ciudad | Notas |
|--------|------------|-----|--------|-------|
| `admin_medellin@sena.edu.co` | `Admin123!` | ADMIN | Medellín | CRUD completo |
| `admin_bogota@sena.edu.co` | `Admin123!` | ADMIN | Bogotá | Sin DELETE |
| `admin@sena.edu.co` | `Admin123!` | ADMIN | Medellín | Compatibilidad tests |
| `usuario@techcorp.co` | `Usuario123!` | USUARIO | Medellín | Solo empleados de su compañía |

### 4.8 Interfaz web de demostración

Ruta raíz: `http://127.0.0.1:8000/` (`templates/index.html`)

- Acceso rápido con las cuentas del seed.
- Muestra rol, ciudad y política activa.
- Deshabilita botones de eliminar para ADMIN Bogotá (coherente con la API).

### 4.9 Pruebas automatizadas relacionadas

| Archivo | Qué valida |
|---------|------------|
| `tests/test_auth_jwt.py` | Registro, login, perfil, roles, `PoliticaAdminCiudad` |
| `tests/test_validation.py` | `test_admin_medellin_has_full_crud`, `test_admin_bogota_restricted_delete_only` |

```powershell
py manage.py test tests.test_auth_jwt tests.test_validation
```

### 4.10 Configuración JWT

En `config/settings.py`:

- `DEFAULT_AUTHENTICATION_CLASSES` → `JwtCustomAuthentication`
- `SIMPLE_JWT` → tiempo de vida del token, algoritmo `HS256`, `SIGNING_KEY`

La clave de firma debe provenir de entorno en producción (no hardcodear secretos).

---

## 5. Pruebas Automatizadas y Rollback Transaccional (Módulo 6)

Se han implementado **26 pruebas automatizadas** que garantizan el correcto funcionamiento del software en todos los escenarios.

Para correr las pruebas:
```powershell
venv\Scripts\python.exe manage.py test
```

### Escenarios de Pruebas Cubiertos
1.  **Servicios y Repositorios:** Creación individual, bulk create, validaciones de negocio.
2.  **Validaciones de Entrada:** Correos duplicados, compañías inexistentes, salarios negativos.
3.  **Seguridad JWT:** Emisión de token correcto, denegación 401 en accesos sin token, expiración.
4.  **Roles y Permisos:** Restricción de borrado por rol, acceso a perfil.
5.  **Política de Propiedad:** Permiso concedido a usuarios de la misma compañía, denegado con 403 Forbidden a usuarios de compañías distintas.
6.  **Rollback Transaccional Obligatorio:** Verificación de que ante un fallo en un listado de empleados en bulk o en la creación de compañía con empleados, no se persiste absolutamente nada.

#### Ejemplo de Flujo de Rollback en Logs:
```text
[2026-05-28 12:49:40] INFO api.controllers.compania_controller | POST /api/companias/con-empleados — TRANSACCIONAL
[2026-05-28 12:49:40] INFO application.services.compania_service | === INICIO TRANSACCIÓN: Crear compañía con empleados ===
[2026-05-28 12:49:40] INFO infrastructure.unit_of_work.unit_of_work | UnitOfWork: Iniciando transacción
[2026-05-28 12:49:40] DEBUG infrastructure.repositories.compania_repository | Repository: Compañía insertada (sin commit explícito) ID=2
[2026-05-28 12:49:40] ERROR application.services.compania_service | === ROLLBACK: Error en transacción — Error de validacion ===
[2026-05-28 12:49:40] ERROR infrastructure.unit_of_work.unit_of_work | UnitOfWork: ROLLBACK — Error tipo=DomainValidationError, mensaje=Error de validacion
[2026-05-28 12:49:40] WARNING api.controllers.compania_controller | Validación de dominio fallida: Error de validacion
[2026-05-28 12:49:40] WARNING django.request | Bad Request: /api/companias/con-empleados
```

---

## 6. Comparación Ampliada con ASP.NET Core

A continuación se muestra una tabla de equivalencias técnicas entre **ASP.NET Core** (C#) y **Django REST Framework** (Python):

| Concepto en ASP.NET Core | Equivalente en Django / DRF | Observaciones |
| :--- | :--- | :--- |
| `IEnumerable<T>` / `List<T>` | QuerySets, Serializers con `many=True` | DRF serializa listas pasando la opción `many=True`. |
| Paginación con `Skip` y `Take` | QuerySet slicing `[offset:limit]` | Python usa slicing nativo en QuerySets que se traduce a `LIMIT/OFFSET`. |
| `async` / `await` + `Task<T>` | Vistas async y ORM async (`abase()`, etc.) | DRF soporta vistas asíncronas, pero su ORM requiere cuidado en transacciones. |
| `DataAnnotations` / `FluentValidation` | Serializers de DRF + Validaciones de Servicio | Estructura en serializers; lógica de negocio compleja en servicios. |
| `xUnit` / `NUnit` + `Moq` | `django.test.TestCase` + `unittest.mock` | TestCase de Django incluye base de datos de pruebas aislada y cliente API. |
| `AddAuthentication().AddJwtBearer()` | `JwtCustomAuthentication` (DRF settings) | Custom authentication backend registrado en `DEFAULT_AUTHENTICATION_CLASSES`. |
| `[Authorize(Roles="ADMIN")]` | Permission class `IsAdmin` | Clases de permiso que sobrescriben `has_permission`. |
| `[Authorize(Policy="...")]` / Handlers | `EsPropietarioDeCompania`, `PoliticaAdminCiudad` | Políticas en `has_permission` / `has_object_permission` según el caso. |
| `ClaimsPrincipal` / `User.Claims` | `request.user` (UsuarioAutenticado) | Inyección de un POPO con propiedades en `request.user` tras validar el JWT. |

---

## 7. Evidencias de Uso de IA (Prompts y Respuestas de Antigravity)

### Prompt 7 - CRUD de colecciones
*   **Pregunta:** Tengo una API REST en Python con Django y Django REST Framework, usando Django ORM, Onion Architecture, Repository Pattern y Unit of Work. Ya existe CRUD individual para Compania y Empleado. Explícame e implementa cómo agregar operaciones sobre colecciones: creación masiva de empleados, actualización parcial con PATCH, eliminación múltiple y listado con paginación, filtrado y ordenamiento. Respeta las capas...
*   **Respuesta de Antigravity:** Se implementaron los métodos `bulk_create_empleados`, `patch_empleado`, `delete_many_empleados` y `get_paginated_empleados` en la capa de servicios y repositorios. La paginación usa slicing del QuerySet, el filtrado usa `Q()` y el ordenamiento traduce dinámicamente los campos. Toda operación de escritura es controlada de principio a fin por el `UnitOfWork` asegurando que no haya commits automáticos en los repositorios.

### Prompt 8 - Programación asíncrona
*   **Pregunta:** En Python con Django y Django ORM, el manejo de peticiones y acceso a datos es síncrono o asíncrono? Explícame qué soporte real ofrece Django para vistas async y ORM async. Si conviene refactorizar...
*   **Respuesta de Antigravity:** Django fue diseñado originalmente de manera síncrona. Aunque ahora soporta vistas asíncronas y adaptadores async para el ORM, mezclarlo con el patrón Unit Of Work basado en transacciones locales e hilos puede romper el aislamiento transaccional y provocar bloqueos en SQLite. Por ello, se justificó técnicamente mantener el esquema síncrono, aplicando optimizaciones de base de datos como `bulk_create` para operaciones por lotes.

### Prompt 9 - Validaciones
*   **Pregunta:** ¿Cuál es el mecanismo de validación recomendado para Django REST Framework? Implementa validaciones para DTOs o serializers de Compania y Empleado...
*   **Respuesta de Antigravity:** El mecanismo estándar en DRF son los Serializers. Sin embargo, para cumplir con Onion Architecture, la validación de formato (sintáctica) se hace en el Serializer (Capa API) y la validación de negocio (semántica, como unicidad de correo, existencia de compañía y salario mayor a cero) se implementa en la capa de Aplicación (`services`), lanzando una excepción `DomainValidationError` que el middleware captura y transforma en una respuesta unificada 400 Bad Request.

### Prompt 10 - Pruebas
*   **Pregunta:** ¿Cuál es el framework de pruebas más usado en Django y DRF? Implementa pruebas unitarias para servicios y repositorios, y pruebas de integración para endpoints de Compania y Empleado...
*   **Respuesta de Antigravity:** El framework estándar es `django.test` (basado en `unittest` de Python) junto con `rest_framework.test.APIClient`. Se escribieron pruebas para toda la aplicación y se incluyó el escenario clave: `test_crear_compania_con_empleados_rollback`, la cual confirma que al ocurrir un fallo en un empleado de la lista, la base de datos revierte tanto la creación de la compañía como de los empleados previos.

### Prompt 11 - JWT por roles
*   **Pregunta:** Explícame e implementa autenticación con JWT en Django REST Framework para este proyecto Onion: entidad Usuario, registro, login que devuelve token y protección de endpoints por roles ADMIN y USUARIO...
*   **Respuesta de Antigravity:** Se utilizó `djangorestframework-simplejwt` pero encapsulando su lógica técnica tras interfaces en la capa `infrastructure`. Se creó la entidad de dominio `Usuario` y un backend personalizado `JwtCustomAuthentication` que decodifica y mapea los claims directamente en un objeto `UsuarioAutenticado` ligero. Las contraseñas se almacenan cifradas en base de datos con `make_password` de Django.

### Prompt 12 - JWT por políticas
*   **Pregunta:** ¿Cuál es la diferencia entre autorización por roles y por políticas en Django REST Framework? Implementa una política de propiedad...
*   **Respuesta:** Los **roles** responden “¿quién eres?” (`ADMIN` vs `USUARIO`). Las **políticas** responden “¿puedes hacer esto sobre este recurso o en estas condiciones?”. Se implementaron dos permission classes en `api/permissions/permissions.py`:
    1. **`EsPropietarioDeCompania`:** un `USUARIO` solo modifica empleados de su `compania_id` (validación en `has_object_permission`).
    2. **`PoliticaAdminCiudad`:** usa el claim JWT `ciudad`. Un `ADMIN` de **Medellín** tiene CRUD completo; un `ADMIN` de **Bogotá** puede consultar y escribir (POST/PUT/PATCH) pero no **DELETE** (403).

---

## 8. Conclusiones de la Parte II
1.  **Flexibilidad de Onion Architecture:** Al agregar JWT y políticas, el dominio permaneció estable; tokens y hash viven en Infrastructure detrás de interfaces (`ITokenService`, `IPasswordHasher`).
2.  **Seguridad desacoplada de `contrib.auth`:** Autenticación propia con `UsuarioAutenticado` y claims personalizados (`rol`, `ciudad`, `compania_id`).
3.  **Roles + políticas combinadas:** El rol define el techo de permisos; las políticas refinan el acceso (propiedad de compañía y ciudad del administrador).
4.  **Transacciones:** El Unit of Work mantiene consistencia en operaciones masivas y en `/api/companias/con-empleados`.

---

## Anexo: guía rápida de autenticación

Documentación detallada adicional: [`.docs/GUIA_AUTH_JWT.md`](.docs/GUIA_AUTH_JWT.md)