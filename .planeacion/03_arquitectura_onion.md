# Onion Architecture

La arquitectura debe respetar:

- Domain
- Application
- Infrastructure
- API

## Regla de dependencias

Las dependencias siempre apuntan hacia el dominio.

Infrastructure depende de Domain.
API depende de Application.
Application depende de Domain.

El dominio NO conoce Django REST Framework.
El dominio NO conoce la base de datos.