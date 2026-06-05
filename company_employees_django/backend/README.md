# Enterprise Hub — Backend (Django REST Framework)

API REST construida bajo **Onion Architecture** con patrones Repository y Unit of Work, autenticación JWT y control de acceso por roles y ciudad.

---

## 🏗️ Arquitectura

El flujo estricto de la Onion Architecture garantiza que las dependencias solo apunten hacia el núcleo (Domain):

```
Controller → Service → UnitOfWork → Repository → ORM → Database
```

### Capas

| Capa | Directorio | Responsabilidad |
|------|-----------|-----------------|
| **Domain** | `domain/` | Entidades puras (`Compania`, `Empleado`, `Usuario`), interfaces, excepciones. Sin dependencias externas. |
| **Application** | `application/` | Servicios de aplicación: orquestan lógica de negocio, delegan en UoW y repositorios. |
| **Infrastructure** | `infrastructure/` | Implementaciones concretas: Django ORM, JWT, hash de contraseñas, migraciones, seed. |
| **API** | `api/` | Controladores DRF, Serializers, Permisos/Políticas. Solo recibe HTTP y delega al Service. |

---

## ⚙️ Configuración y Ejecución

### 1. Variables de entorno
El archivo `.env` ya está incluido con valores de desarrollo:
```ini
SECRET_KEY=tu-clave-secreta-django
JWT_SECRET_KEY=tu-clave-para-jwt
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Migraciones y datos de prueba
```bash
python manage.py migrate
python manage.py seed
```

### 4. Arrancar servidor
```bash
python manage.py runserver
```
El frontend estará disponible en **http://127.0.0.1:8000** (Django sirve los templates de `/frontend` directamente).

---

## 🔐 Sistema de Autenticación y Permisos

### JWT Personalizado
- `POST /api/auth/login` devuelve un token JWT firmado con `HS256`.
- El token contiene los claims: `user_id`, `correo`, `rol`, `ciudad`, `compania_id`.
- `JwtCustomAuthentication` (en `infrastructure/security/`) decodifica el token y construye `request.user` sin usar `django.contrib.auth.User`.

### Permisos por Rol
| Permission Class | Qué permite |
|-----------------|-------------|
| `IsAuthenticatedUser` | Cualquier usuario con token válido |
| `IsAdminOrUsuario` | Rol ADMIN o USUARIO |
| `IsAdmin` | Solo rol ADMIN |

### Políticas por Ciudad (`PoliticaAdminCiudad`)
| Ciudad del ADMIN | GET | POST/PUT/PATCH | DELETE |
|-----------------|:---:|:--------------:|:------:|
| **Medellín** | ✅ | ✅ | ✅ |
| **Bogotá** | ✅ | ✅ | ❌ 403 |

### Política de Propiedad (`EsPropietarioDeCompania`)
Un usuario con rol `USUARIO` solo puede modificar empleados cuya `compania_id` coincide con la suya (registrada en el token JWT).

---

## 📋 Endpoints Completos

### Auth
```
POST  /api/auth/registro
POST  /api/auth/login
GET   /api/auth/perfil
```

### Compañías
```
GET    /api/companias               ← Paginado: ?pagina=1&tamano=25&buscar=tech
GET    /api/companias/{id}
POST   /api/companias
PUT    /api/companias/{id}          ← Solo Bogotá (PoliticaAdminCiudad)
PATCH  /api/companias/{id}          ← Solo Bogotá
DELETE /api/companias/{id}          ← Solo Medellín
GET    /api/companias/{id}/empleados
POST   /api/companias/con-empleados ← TRANSACCIONAL (ADMIN)
```

### Empleados
```
GET    /api/empleados               ← Paginado: ?pagina=1&tamano=25&buscar=garcia
GET    /api/empleados/{id}
POST   /api/empleados
PUT    /api/empleados/{id}          ← Solo Bogotá
PATCH  /api/empleados/{id}          ← Solo Bogotá
DELETE /api/empleados/{id}          ← Solo Medellín
POST   /api/empleados/bulk          ← Carga masiva ({ "empleados": [...] })
DELETE /api/empleados/bulk-delete   ← Eliminación masiva ({ "ids": [1,2,3] })
```

---

## 🔄 Endpoint Transaccional: `POST /api/companias/con-empleados`

Crea una compañía y todos sus empleados en **una sola transacción atómica**. Si algún empleado falla las validaciones de negocio (correo duplicado, salario ≤ 0, etc.), se hace **rollback completo** — ni la compañía ni ningún empleado quedan guardados.

**Body de ejemplo:**
```json
{
  "nombre": "Nueva Corp SAS",
  "direccion": "Calle 100 # 45-20",
  "telefono": "+57 601 555-0001",
  "empleados": [
    {
      "nombre": "Ana",
      "apellido": "García",
      "correo": "ana.garcia@nuevacorp.co",
      "cargo": "Desarrolladora Senior",
      "salario": 8500000
    }
  ]
}
```

**Flujo interno:**
```
CompaniaConEmpleadosController
  → CompaniaConEmpleadosSerializer (valida estructura)
  → CompaniaService.create_compania_con_empleados()
    → UnitOfWork (abre transaction.atomic)
      → CompaniaRepository.create()
      → EmpleadoRepository.create() × N
    → UnitOfWork.commit()   ← Si todo OK
    → UnitOfWork.rollback() ← Si algo falla
```

---

## 🧪 Pruebas Automatizadas

```bash
python manage.py test
```

Suite con más de 26 pruebas que cubren:
- CRUD de compañías y empleados
- Validaciones de negocio (correo único, salario positivo, compañía existente)
- Seguridad JWT (token inválido → 401, rol incorrecto → 403)
- `PoliticaAdminCiudad` (admin Bogotá no puede DELETE)
- `EsPropietarioDeCompania` (usuario no puede editar empleados ajenos)
- **Rollback transaccional** (fallo en empleado revierte toda la operación)

---

## 📝 Logging

Cada operación registra en `logs/app.log`:
- Inicio de la aplicación
- Cada petición HTTP relevante
- Inicio de transacción, commit y rollback
- Errores de validación y excepciones

---

## 👤 Usuarios Seed

```bash
python manage.py seed
```

| Correo | Contraseña | Rol | Ciudad |
|--------|------------|-----|--------|
| `admin_medellin@sena.edu.co` | `Admin123!` | ADMIN | Medellín |
| `admin_bogota@sena.edu.co` | `Admin123!` | ADMIN | Bogotá |
| `admin@sena.edu.co` | `Admin123!` | ADMIN | Medellín |
| `usuario@techcorp.co` | `Usuario123!` | USUARIO | Medellín |
