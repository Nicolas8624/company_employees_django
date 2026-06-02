# Preguntas y respuestas para sustentacion

## 1. Que diferencia hay entre operar sobre un objeto y sobre una coleccion?

Un objeto es un recurso individual, por ejemplo `/api/empleados/5`. Una coleccion representa varios recursos, por ejemplo `/api/empleados`. En colecciones se usan operaciones como creacion masiva, eliminacion multiple, paginacion, filtrado y ordenamiento.

## 2. Como se garantiza que una creacion masiva sea una sola transaccion?

La operacion se ejecuta dentro del `UnitOfWork`, que usa `transaction.atomic` de Django. Si todos los registros se crean correctamente, la transaccion se confirma. Si uno falla, Django revierte toda la operacion y no quedan datos parciales.

## 3. Por que es importante la paginacion?

Porque evita devolver miles de registros en una sola respuesta. Esto mejora rendimiento, consumo de memoria y experiencia del cliente.

## 4. Django soporta asincronia real?

Django soporta vistas async y tiene soporte async parcial en el ORM moderno. Sin embargo, no todo el ecosistema es completamente async, y las transacciones con `transaction.atomic` requieren cuidado. Por eso se debe justificar si se implementa async o si se conserva el modelo sincrono por seguridad transaccional.

## 5. Donde se ubican las validaciones?

Las validaciones de formato de entrada se pueden hacer con serializers de DRF, pero las reglas de negocio importantes deben estar en la capa Application, por ejemplo correo unico, compania existente o salario positivo.

## 6. Que es JWT?

JWT es un token firmado que contiene claims sobre el usuario, como id, correo, rol, ciudad, compania_id y expiracion. El cliente lo envia en el header `Authorization: Bearer <token>` y la API lo valida en cada peticion mediante `JwtCustomAuthentication`.

## 6.1. Que claims usa este proyecto?

- `user_id`, `correo`, `rol`, `ciudad`, `compania_id` (opcional), `exp`.

## 6.2. Cual es la diferencia entre rol ADMIN de Medellin y Bogota?

Ambos son ADMIN a nivel de rol (pueden crear y actualizar). La politica `PoliticaAdminCiudad` lee el claim `ciudad`:

- **Medellin:** CRUD completo, incluido DELETE.
- **Bogota:** puede GET, POST, PUT y PATCH, pero DELETE devuelve 403.

## 7. Por que no se guarda la contrasena en texto plano?

Porque seria un riesgo grave de seguridad. Se guarda un hash generado con un algoritmo seguro. En el login se compara la contrasena ingresada contra ese hash.

## 8. Cual es la diferencia entre roles y politicas?

Los roles responden que tipo de usuario es alguien, por ejemplo ADMIN o USUARIO. Las politicas evaluan reglas mas especificas, por ejemplo si el usuario pertenece a la misma compania del empleado que intenta editar.

## 9. Como funciona la politica de propiedad?

La politica revisa el rol y la compania del usuario autenticado. Si es ADMIN, permite la accion. Si es USUARIO, solo permite modificar empleados cuya `compania_id` coincida con la compania del usuario.

## 10. Como se compara con ASP.NET Core?

En ASP.NET Core se usaria `[Authorize(Roles="ADMIN")]` para roles y `[Authorize(Policy="EsPropietario")]` o `[Authorize(Policy="AdminCiudad")]` para politicas. En Django REST Framework se logra con permission classes (`IsAdmin`, `EsPropietarioDeCompania`, `PoliticaAdminCiudad`), validando claims del JWT y, si aplica, el objeto del recurso.

## 9. Donde esta documentado el login y las politicas?

- `README_PARTE_II.md` — seccion 4 (resumen tecnico).
- `.docs/GUIA_AUTH_JWT.md` — guia paso a paso con ejemplos curl y matriz de permisos.

## 11. Como se mantiene Onion Architecture?

El dominio no depende de Django. La aplicacion usa interfaces y servicios. La infraestructura implementa repositorios y acceso a base de datos. La API solo recibe peticiones, valida datos y delega a los servicios. Los repositorios no controlan commits; eso lo hace el Unit of Work.

## 12. Que prueba demuestra el rollback?

Una prueba crea una compania con varios empleados, pero uno contiene datos invalidos. Se espera una excepcion o error controlado. Despues se verifica que la cantidad de companias y empleados en la base de datos no cambio.
