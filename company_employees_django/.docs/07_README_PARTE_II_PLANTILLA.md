# Plantilla para actualizar README - Parte II

## CRUD de colecciones

En esta fase se agregaron operaciones sobre colecciones para complementar el CRUD individual existente.

Endpoints:

```http
POST /api/empleados/bulk
PATCH /api/empleados/{id}
DELETE /api/empleados/bulk-delete
GET /api/empleados?pagina=1&tamano=10&orden=apellido&dir=asc&buscar=gomez
```

Explicar:

- Como funciona bulk insert.
- Como se garantiza la transaccion con Unit of Work.
- Como funciona PATCH.
- Como se elimina una lista de IDs.
- Como se pagina, filtra y ordena.

## Programacion asincrona

### Mi tecnologia soporta async?

Django soporta vistas asincronas y versiones modernas tienen soporte parcial para ORM async. Sin embargo, el proyecto usa Unit of Work con `transaction.atomic`, por lo que se debe tener cuidado para no romper el control transaccional.

Decision tomada:

```text
Se determinó mantener el modelo sincrónico en este stack.
Justificación:
1. **Unit of Work y Transacciones**: Django ORM tradicionalmente utiliza conexiones y transacciones sincrónicas. Aunque versiones recientes (Django 4.1+) incluyen métodos como `aatomic()`, mezclar código asíncrono con el patrón Unit Of Work puede causar comportamientos inesperados, pérdida de contexto transaccional, y problemas de deadlocks.
2. **Base de datos**: SQLite (utilizado para propósitos académicos aquí) maneja de forma ineficiente la concurrencia de escrituras asíncronas, lo que elimina cualquier beneficio potencial de rendimiento en operaciones Write-heavy.
3. **Onion Architecture**: Refactorizar repositorios enteros a `async def` sin un beneficio real de I/O de red perjudicaría la legibilidad y forzaría la reescritura de los services, interfaces y serializers (ya que DRF no tiene soporte completo para vistas puras asíncronas en todas sus versiones/extensiones).
```

### Que se refactorizo o alternativa aplicada

```text
No se refactorizó hacia asíncrono puro. Se mantuvo el diseño robusto, sincrónico y seguro transaccionalmente (ACID). Para operaciones masivas, se implementó optimización por lotes (`bulk_create`, `filter().delete()`) que maximiza el rendimiento bajo el esquema síncrono.
```

## Validaciones

Libreria o mecanismo usado:

```text
Django REST Framework serializers + validaciones en capa Application.
```

Reglas aplicadas:

- Campos obligatorios.
- Longitudes maximas.
- Correo valido.
- Correo unico.
- Salario positivo.
- Compania existente.

Formato de error:

```json
{
  "mensaje": "Error de validacion",
  "errores": [
    {
      "campo": "correo",
      "detalle": "El correo ya existe"
    }
  ]
}
```

## Pruebas

Comando:

```powershell
python manage.py test
```

Se probaron:

- Servicios.
- Repositorios.
- Endpoints.
- Validaciones.
- JWT.
- Roles.
- Politicas.
- Rollback transaccional.

### Prueba del rollback transaccional

Explicar el caso:

```text
Se intenta crear una compania con varios empleados, pero uno de ellos es invalido. La prueba confirma que no queda guardada ni la compania ni ningun empleado parcial.
```

## Seguridad

### Autenticacion con JWT

Endpoints:

```http
POST /api/auth/registro
POST /api/auth/login
GET /api/auth/perfil
```

El login devuelve un token JWT con claims:

- id de usuario (`user_id`).
- correo.
- rol.
- ciudad.
- compania_id (opcional).
- expiracion.

### Autorizacion por roles

Roles:

- `ADMIN`
- `USUARIO`

Reglas:

- GET: usuario autenticado.
- POST/PUT/PATCH: ADMIN o USUARIO.
- DELETE: solo ADMIN.
- Endpoint transaccional: solo ADMIN.

### Autorizacion por politicas

Politicas implementadas:

```text
EsPropietarioDeCompania
PoliticaAdminCiudad
```

Reglas:

- **EsPropietarioDeCompania:** ADMIN sin restriccion; USUARIO solo edita empleados de su `compania_id`.
- **PoliticaAdminCiudad:** ADMIN de Medellin = CRUD completo; ADMIN de Bogota = sin DELETE (403).

## Variables de entorno

Ejemplo:

```env
DJANGO_SECRET_KEY=...
JWT_SECRET_KEY=...
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
DEBUG=True
```

## Comparacion ampliada con ASP.NET Core

| Concepto en ASP.NET Core | Equivalente en Django/DRF |
|---|---|
| Endpoints de coleccion `IEnumerable/List` | APIViews/serializers con `many=True` |
| Paginacion `Skip/Take` | QuerySets con slicing o Paginator |
| `async/await` + `Task<T>` | Vistas async y ORM async parcial |
| DataAnnotations/FluentValidation | DRF serializers + validadores de aplicacion |
| xUnit/NUnit + Moq | Django TestCase, DRF APIClient, unittest.mock |
| `AddAuthentication().AddJwtBearer()` | DRF SimpleJWT o middleware JWT |
| `[Authorize(Roles="ADMIN")]` | Permission classes por rol |
| `[Authorize(Policy="...")]` | Permission classes/policies con `has_object_permission` |
| `ClaimsPrincipal/Claims` | Claims del JWT y usuario autenticado en request |

## Conclusiones de la Parte II

En esta segunda parte se evoluciono la API hacia una solucion mas cercana a produccion, agregando operaciones sobre colecciones, validaciones, pruebas, seguridad con JWT, autorizacion por roles y politicas, manteniendo la separacion por capas de Onion Architecture.
