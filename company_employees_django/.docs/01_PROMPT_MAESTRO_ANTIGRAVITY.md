# Prompt maestro para Antigravity

Actua como un desarrollador senior de Python, Django y Django REST Framework. Necesito que continues un proyecto existente de API REST para companias y empleados hecho con Onion Architecture, Repository Pattern y Unit of Work.

No crees un proyecto nuevo. Trabaja sobre el proyecto existente.

Contexto del proyecto actual:

- Framework: Django + Django REST Framework.
- Base de datos: SQLite.
- Capas actuales:
  - `domain`: entidades puras e interfaces.
  - `application`: servicios de aplicacion.
  - `infrastructure`: modelos Django ORM, repositorios concretos, Unit of Work, seed.
  - `api`: controllers, serializers, routes y middlewares.
- Flujo obligatorio:

```text
Controller -> Service -> UnitOfWork -> Repository -> ORM -> Database
```

Objetivo:

Implementar la Parte II de la actividad SENA sobre la API ya construida, agregando:

1. CRUD de colecciones:
   - Bulk insert.
   - PATCH parcial.
   - Eliminacion multiple.
   - Listados con paginacion, filtrado y ordenamiento.
2. Programacion asincrona o justificacion tecnica si Django ORM del proyecto no se adapta completamente a async.
3. Validaciones:
   - Campos obligatorios.
   - Longitudes.
   - Correo valido.
   - Salario positivo.
   - Regla de negocio: correo unico o existencia de compania.
   - Respuesta uniforme para errores de validacion.
4. Pruebas:
   - Unitarias para servicios.
   - Integracion para endpoints.
   - Prueba obligatoria de rollback transaccional.
5. Seguridad JWT por roles:
   - Registro.
   - Login.
   - Perfil.
   - Token JWT.
   - Roles `ADMIN` y `USUARIO`.
   - Endpoints protegidos segun rol.
6. Seguridad JWT por politicas:
   - Al menos politica de propiedad: un usuario solo puede editar/eliminar empleados de su propia compania, excepto ADMIN.
   - Opcional: limite de salario solo para ADMIN.
7. README actualizado y evidencia de prompts.

Reglas de arquitectura:

- `domain` no puede importar Django, DRF ni infraestructura.
- `application` no puede usar Django ORM directamente.
- `infrastructure` implementa interfaces del dominio.
- `api` recibe HTTP, valida entrada y delega a servicios.
- Los repositorios no deben confirmar transacciones.
- El Unit of Work controla las transacciones.
- La clave JWT debe leerse desde variable de entorno o settings, no estar quemada en el codigo.
- Las contrasenas deben guardarse con hash, nunca texto plano.

Antes de modificar:

1. Lee la estructura del proyecto.
2. Identifica los archivos existentes.
3. Propone un plan breve por modulos.
4. Implementa modulo por modulo.
5. Ejecuta pruebas despues de cada modulo cuando sea posible.

Entrega esperada:

- Codigo funcionando.
- Migraciones necesarias.
- Tests actualizados.
- README actualizado.
- Explicacion corta de como se mantiene Onion Architecture.
- Tabla comparativa Django vs ASP.NET Core.
