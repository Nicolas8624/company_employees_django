# Requisitos de la actividad Parte II

La actividad pide evolucionar la API REST de la Parte I. No se debe reiniciar el proyecto.

## Modulo 1 - CRUD completo de objetos y colecciones

Implementar:

- Creacion masiva de empleados.
- Actualizacion parcial con `PATCH`.
- Eliminacion multiple por lista de IDs.
- Listado avanzado con:
  - `pagina`
  - `tamano`
  - `orden`
  - `dir`
  - `buscar`

Ejemplo:

```http
GET /api/empleados?pagina=1&tamano=10&orden=apellido&dir=asc&buscar=gomez
```

Respuesta esperada para listados:

```json
{
  "datos": [],
  "pagina": 1,
  "tamano": 10,
  "total": 0,
  "total_paginas": 0
}
```

## Modulo 2 - Programacion asincrona

Investigar y documentar:

- Django soporta vistas async.
- Django ORM tiene soporte async parcial en versiones modernas, pero muchas operaciones siguen dependiendo de transacciones y conexiones sync.
- Si se refactoriza a async, hacerlo con cuidado en repositorios, servicios y Unit of Work.
- Si no se implementa async completo, documentar la justificacion tecnica.

Entrega minima aceptable:

- Seccion en README explicando si aplica async en este stack.
- Evidencia de investigacion.
- Si se implementa, agregar endpoints o servicios async donde sea seguro.

## Modulo 3 - Validaciones

Validaciones minimas:

- `nombre`: obligatorio, no vacio, longitud maxima.
- `apellido`: obligatorio, no vacio, longitud maxima.
- `correo`: obligatorio, formato email, unico.
- `cargo`: obligatorio.
- `salario`: mayor que cero.
- `compania_id`: debe existir.
- Para bulk: validar todos los items antes de confirmar.

Formato uniforme de error:

```json
{
  "mensaje": "Error de validacion",
  "errores": [
    {
      "campo": "correo",
      "detalle": "Formato de correo invalido"
    }
  ]
}
```

Codigo HTTP recomendado: `400 Bad Request` o `422 Unprocessable Entity`.

## Modulo 4 - Pruebas

Probar:

- Servicios de compania y empleado.
- Repositorios.
- Endpoints principales.
- Listado paginado.
- Creacion masiva.
- PATCH.
- Eliminacion multiple.
- Validaciones.
- Login y proteccion JWT.
- Politica de propiedad.
- Rollback transaccional obligatorio.

Comando esperado:

```powershell
python manage.py test
```

## Modulo 5 - JWT por roles

Agregar entidad Usuario:

- id
- nombre
- correo unico
- contrasena_hash
- rol: `ADMIN` o `USUARIO`
- compania_id opcional
- fecha_creacion

Endpoints:

```http
POST /api/auth/registro
POST /api/auth/login
GET  /api/auth/perfil
```

Proteccion minima:

- GET listar/consultar: cualquier usuario autenticado.
- POST/PUT/PATCH: `ADMIN` o `USUARIO`.
- DELETE: solo `ADMIN`.
- POST `/api/companias/con-empleados`: solo `ADMIN`.

## Modulo 6 - JWT por politicas

Implementar al menos:

`EsPropietarioDeCompania`

Regla:

- Si el usuario es `ADMIN`, puede todo (respecto a compania).
- Si el usuario es `USUARIO`, solo puede actualizar empleados cuya `compania_id` coincida con la del token.

`PoliticaAdminCiudad` (claim `ciudad` en JWT):

- ADMIN **Medellin:** CRUD completo.
- ADMIN **Bogota:** todo excepto DELETE.

Documentacion detallada: `.docs/GUIA_AUTH_JWT.md`

Opcional:

`LimiteSalario`

- Solo `ADMIN` puede asignar salarios por encima de un umbral definido.

## Producto final

- Codigo fuente actualizado.
- Endpoints funcionando.
- Validaciones.
- Pruebas.
- JWT con roles.
- Politica aplicada.
- README actualizado.
- Evidencia de uso de IA.
- Comparacion con ASP.NET Core.
- Preparacion para sustentacion.
