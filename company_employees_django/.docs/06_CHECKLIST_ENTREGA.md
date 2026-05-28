# Checklist de entrega Parte II

## CRUD de colecciones

- [ ] `POST /api/empleados/bulk`
- [ ] `PATCH /api/empleados/{id}`
- [ ] `DELETE /api/empleados/bulk-delete`
- [ ] `GET /api/empleados` con `pagina`, `tamano`, `orden`, `dir`, `buscar`
- [ ] Respuesta paginada tipo envelope
- [ ] Operaciones masivas dentro de Unit of Work

## Async

- [ ] Se investigo soporte async en Django
- [ ] Se documento decision en README
- [ ] Si se implemento async, se probo que no rompe transacciones
- [ ] Si no se implemento async completo, hay justificacion tecnica

## Validaciones

- [ ] Campos obligatorios
- [ ] Longitudes maximas
- [ ] Correo valido
- [ ] Correo unico
- [ ] Salario positivo
- [ ] Compania existente
- [ ] Errores con formato uniforme
- [ ] Codigo HTTP adecuado: 400 o 422

## Pruebas

- [ ] Pruebas unitarias de servicios
- [ ] Pruebas de repositorios
- [ ] Pruebas de endpoints
- [ ] Prueba de listado paginado
- [ ] Prueba de bulk insert
- [ ] Prueba de PATCH
- [ ] Prueba de eliminacion multiple
- [ ] Prueba de validaciones
- [ ] Prueba de rollback transaccional
- [ ] Pruebas JWT
- [ ] Pruebas de roles
- [ ] Pruebas de politica ownership

## JWT por roles

- [ ] Entidad Usuario
- [ ] Modelo ORM Usuario
- [ ] Repositorio Usuario
- [ ] AuthService
- [ ] Hash de contrasena
- [ ] Registro
- [ ] Login
- [ ] Perfil
- [ ] Token con claims: id, correo, rol, compania_id, exp
- [ ] SECRET_KEY JWT por variable de entorno/settings
- [ ] GET protegido con autenticacion
- [ ] DELETE protegido solo ADMIN
- [ ] Endpoint transaccional protegido solo ADMIN

## Politicas

- [ ] Politica `EsPropietarioDeCompania`
- [ ] ADMIN puede todo
- [ ] USUARIO solo puede editar/eliminar empleados de su compania
- [ ] Caso permitido probado
- [ ] Caso denegado probado con 403

## Documentacion

- [ ] README actualizado
- [ ] Comandos de instalacion
- [ ] Comandos de migracion
- [ ] Comando de tests
- [ ] Variables de entorno
- [ ] Ejemplos de endpoints
- [ ] Comparacion con ASP.NET Core
- [ ] Conclusiones Parte II
- [ ] Evidencia de prompts 7 a 12
- [ ] Capturas en Postman/Thunder Client/Swagger o equivalente

## Reglas que no se pueden romper

- [ ] Controllers no usan ORM directo
- [ ] Repositories no hacen commit
- [ ] Domain no depende de Django
- [ ] Application no depende del ORM
- [ ] Password nunca en texto plano
- [ ] JWT secret no quemado en codigo
- [ ] Endpoints sensibles protegidos
