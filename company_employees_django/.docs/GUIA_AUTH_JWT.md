# Guía de autenticación JWT — Roles, claims y políticas

Documentación de referencia para la Parte II del proyecto **Company Employees Django**.

---

## 1. ¿Qué se implementó?

| Funcionalidad | Estado |
|---------------|--------|
| Login con correo y contraseña | Implementado |
| Registro de usuarios | Implementado |
| Token JWT con claims personalizados | Implementado |
| Protección de endpoints por rol | Implementado |
| Política de propiedad de compañía | Implementado |
| Política de ciudad (Medellín vs Bogotá) | Implementado |
| UI de demostración (`/`) | Implementado |
| Pruebas automatizadas | Implementado |

---

## 2. Puesta en marcha

```powershell
cd company_employees_django
# Activar entorno virtual si aplica
pip install -r requirements.txt
py manage.py migrate
py manage.py seed
py manage.py runserver
```

- API: `http://127.0.0.1:8000/api/`
- Panel demo: `http://127.0.0.1:8000/`

---

## 3. Endpoints de autenticación

### 3.1 Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "correo": "admin_medellin@sena.edu.co",
  "password": "Admin123!"
}
```

Respuesta exitosa (`200`):

```json
{
  "usuario": {
    "id": 2,
    "correo": "admin_medellin@sena.edu.co",
    "rol": "ADMIN",
    "ciudad": "Medellín",
    "compania_id": null
  },
  "token": "<JWT_ACCESS_TOKEN>"
}
```

Errores comunes:

| Código | Causa |
|--------|-------|
| `400` | Falta correo o contraseña; credenciales inválidas |
| `401` | Token ausente o inválido en rutas protegidas |

### 3.2 Registro

```http
POST /api/auth/registro
Content-Type: application/json

{
  "correo": "admin.nuevo@ejemplo.com",
  "password": "Pass123!",
  "rol": "ADMIN",
  "ciudad": "Bogotá"
}
```

Usuario estándar (requiere compañía existente):

```json
{
  "correo": "empleado@techcorp.co",
  "password": "Pass123!",
  "rol": "USUARIO",
  "ciudad": "Medellín",
  "compania_id": 1
}
```

### 3.3 Perfil

```http
GET /api/auth/perfil
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

---

## 4. Cómo usar el token

Todas las rutas de compañías y empleados (excepto login/registro) requieren:

```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

Ejemplo con curl:

```bash
curl -X GET "http://127.0.0.1:8000/api/empleados?pagina=1&tamano=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 5. Claims del JWT

| Claim | Origen | Uso |
|-------|--------|-----|
| `user_id` | Base de datos | Identificar usuario |
| `correo` | Base de datos | Perfil / auditoría |
| `rol` | Base de datos | `IsAdmin`, `IsAdminOrUsuario` |
| `ciudad` | Base de datos | `PoliticaAdminCiudad` |
| `compania_id` | Base de datos (opcional) | `EsPropietarioDeCompania` |
| `exp` | SimpleJWT | Expiración del token |

Generación: `infrastructure/security/token_service.py`  
Validación: `infrastructure/security/jwt_authentication.py`

---

## 6. Autorización por roles

### ADMIN

- Listar y consultar recursos.
- Crear y actualizar compañías y empleados.
- Eliminar recursos **solo si la política de ciudad lo permite** (ver sección 7).
- Endpoint transaccional `POST /api/companias/con-empleados`.

### USUARIO

- Listar y consultar.
- Crear empleados y actualizar empleados **de su compañía**.
- **No** puede `DELETE`.
- **No** puede `POST /api/companias/con-empleados`.

---

## 7. Política de ciudad (`PoliticaAdminCiudad`)

Regla de negocio acordada:

| Administrador | GET | POST | PUT | PATCH | DELETE |
|---------------|-----|------|-----|-------|--------|
| **Medellín** | Sí | Sí | Sí | Sí | Sí |
| **Bogotá** | Sí | Sí | Sí | Sí | **No** |

Implementación: `api/permissions/permissions.py` → clase `PoliticaAdminCiudad`.

- Solo aplica cuando `rol == ADMIN`.
- Normaliza `ciudad` sin tildes (`Bogotá` = `bogota`).
- Bloquea únicamente el método HTTP `DELETE`.

Ejemplo — ADMIN Bogotá intenta eliminar empleado:

```http
DELETE /api/empleados/5
Authorization: Bearer <token_admin_bogota>
```

Respuesta: `403 Forbidden`

```json
{
  "detail": "Acceso restringido: los administradores de Bogotá no pueden eliminar recursos (operación DELETE no permitida)."
}
```

Ejemplo — ADMIN Bogotá crea compañía (permitido):

```http
POST /api/companias
Authorization: Bearer <token_admin_bogota>
Content-Type: application/json

{
  "nombre": "Nueva Empresa",
  "direccion": "Calle 1",
  "telefono": "3001234567"
}
```

Respuesta: `201 Created`

---

## 8. Política de propiedad (`EsPropietarioDeCompania`)

| Rol | Regla |
|-----|-------|
| ADMIN | Sin restricción por compañía |
| USUARIO | Solo `PUT`/`PATCH` en empleados con el mismo `compania_id` del token |

Aplica en `EmpleadoDetailController` para actualizaciones.

---

## 9. Usuarios del seed

| Correo | Contraseña | Rol | Ciudad | Para probar |
|--------|------------|-----|--------|-------------|
| `admin_medellin@sena.edu.co` | `Admin123!` | ADMIN | Medellín | DELETE permitido |
| `admin_bogota@sena.edu.co` | `Admin123!` | ADMIN | Bogotá | DELETE bloqueado |
| `usuario@techcorp.co` | `Usuario123!` | USUARIO | Medellín | Solo su compañía |

---

## 10. Escenarios de prueba manual

### Escenario A — ADMIN Medellín elimina empleado

1. Login con `admin_medellin@sena.edu.co`.
2. `DELETE /api/empleados/{id}` con Bearer token.
3. Esperado: `204 No Content`.

### Escenario B — ADMIN Bogotá no puede eliminar

1. Login con `admin_bogota@sena.edu.co`.
2. `DELETE /api/empleados/{id}`.
3. Esperado: `403 Forbidden`.

### Escenario C — ADMIN Bogotá sí puede crear

1. Mismo token de Bogotá.
2. `POST /api/companias` con JSON válido.
3. Esperado: `201 Created`.

### Escenario D — USUARIO de otra compañía

1. Login con `usuario@techcorp.co` (compañía 1).
2. `PATCH /api/empleados/{id_de_otra_compania}`.
3. Esperado: `403 Forbidden`.

---

## 11. Pruebas automatizadas

```powershell
py manage.py test tests.test_auth_jwt tests.test_validation
```

Clases relevantes:

- `AuthRegistroLoginTests`
- `RolePermissionTests`
- `EsPropietarioDeCompaniaTests`
- `PoliticaAdminCiudadTests`
- `ValidationTests.test_admin_medellin_has_full_crud`
- `ValidationTests.test_admin_bogota_restricted_delete_only`

---

## 12. Archivos modificados o clave en esta entrega

| Archivo | Cambio |
|---------|--------|
| `api/permissions/permissions.py` | Política Bogotá: bloqueo de DELETE (no POST/PUT) |
| `api/controllers/auth_controller.py` | Perfil con `IsAuthenticatedUser` |
| `application/services/auth_service.py` | Login/registro con `ciudad` |
| `infrastructure/security/token_service.py` | Claim `ciudad` en JWT |
| `infrastructure/security/jwt_authentication.py` | `UsuarioAutenticado.ciudad` |
| `domain/entities/usuario.py` | Campo `ciudad` |
| `infrastructure/database/models.py` | `UsuarioModel.ciudad` |
| `infrastructure/seed/.../seed.py` | Usuarios Medellín y Bogotá |
| `templates/index.html` | UI alineada con política DELETE |
| `tests/test_auth_jwt.py` | Pruebas de política por ciudad |
| `tests/test_validation.py` | Pruebas POST/PUT vs DELETE Bogotá |

---

## 13. Sustentación oral (resumen)

1. **Login** valida credenciales en `AuthService` y devuelve JWT.
2. **Roles** (`ADMIN`/`USUARIO`) definen el alcance general.
3. **Claims** (`ciudad`, `compania_id`) permiten políticas finas sin consultar BD en cada request.
4. **Política de propiedad** protege datos entre compañías.
5. **Política de ciudad** diferencia administradores Medellín (CRUD) y Bogotá (sin eliminar).
6. Todo respeta **Onion Architecture**: controllers delgados, lógica en services, permisos en API, JWT en infrastructure.
