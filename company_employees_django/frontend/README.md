# Enterprise Hub — Frontend (SPA)

Interfaz web de usuario construida en **HTML5, CSS3 y JavaScript Vanilla**, diseñada con estética *dark mode glassmorphism* y control de permisos dinámico por ciudad del usuario autenticado.

---

## 🗂️ Estructura de Archivos

```text
frontend/
├── login.html          ← Pantalla de inicio de sesión
├── index.html          ← Dashboard principal (CRUD completo)
├── css/
│   └── styles.css      ← Sistema de diseño completo (tokens, componentes, animaciones)
└── js/
    ├── storage.js      ← Gestión de sesión en LocalStorage
    ├── auth.js         ← Login, logout, protección de rutas
    ├── permissions.js  ← Reglas de negocio por ciudad (Medellín / Bogotá)
    ├── api.js          ← Cliente HTTP centralizado con Bearer Token automático
    └── dashboard.js    ← Lógica CRUD, tabs, modales y consola HTTP en vivo
```

---

## 🔄 Orden de Carga de Scripts

El orden de los `<script>` en cada HTML es crítico:

```html
<!-- index.html -->
<script src="/static/js/storage.js"></script>      <!-- 1: sesión -->
<script src="/static/js/permissions.js"></script>  <!-- 2: reglas -->
<script src="/static/js/api.js"></script>           <!-- 3: HTTP (usa Storage) -->
<script src="/static/js/auth.js"></script>          <!-- 4: auth (usa Api + Storage) -->
<script src="/static/js/dashboard.js"></script>     <!-- 5: UI (usa todo lo anterior) -->
```

---

## 📦 Módulos JavaScript

### `storage.js`
Centraliza toda la persistencia del lado cliente.
- `Storage.saveSession(token, user)` — guarda JWT y datos del usuario
- `Storage.getToken()` — recupera el token para las peticiones
- `Storage.getUser()` — recupera el objeto usuario parseado
- `Storage.clearSession()` — limpia al cerrar sesión
- `Storage.hasSession()` — verifica si hay sesión activa

### `auth.js`
Maneja el flujo de autenticación y protección de rutas.
- `Auth.requireAuth()` — redirige a `/login` si no hay token (usado en `index.html`)
- `Auth.redirectIfAuthenticated()` — redirige a `/` si ya hay sesión (usado en `login.html`)
- `Auth.login(correo, password)` — llama a `POST /api/auth/login`, guarda sesión
- `Auth.logout()` — limpia sesión y redirige a login
- `Auth.verifySession()` — valida el token con `GET /api/auth/perfil`; si falló, cierra sesión

### `permissions.js`
Implementa las **reglas de negocio por ciudad** sin contactar la API:

| Método | Medellín | Bogotá |
|--------|:--------:|:------:|
| `canGet(user)` | ✅ | ✅ |
| `canPost(user)` | ✅ | ✅ |
| `canBulk(user)` | ✅ | ✅ |
| `canPut(user)` | ❌ | ✅ |
| `canPatch(user)` | ❌ | ✅ |
| `canDelete(user)` | ✅ | ❌ |

También incluye `getPolicyDescription(user)` y `getDeniedMessage(action, user)` para mensajes de UI.

### `api.js`
Cliente HTTP centralizado. Todos los métodos devuelven `{ ok, status, data }`.

**Agrega automáticamente** el header `Authorization: Bearer <token>` en cada petición.

Métodos disponibles:
- Auth: `login`, `getPerfil`
- Compañías: `getCompanias`, `getCompaniaById`, `createCompania`, `updateCompania`, `patchCompania`, `deleteCompania`, **`createCompaniaConEmpleados`**
- Empleados: `getEmpleados`, `getEmpleadoById`, `createEmpleado`, `updateEmpleado`, `patchEmpleado`, `deleteEmpleado`, `bulkCreateEmpleados`

También emite eventos `api:request` y `api:response` usados por la consola HTTP en vivo.

### `dashboard.js`
Controlador principal del dashboard. Responsabilidades:
- Inicialización: verifica sesión, renderiza perfil, aplica permisos a la UI
- **Tabs**: `switchTab('companias')` / `switchTab('empleados')`
- **CRUD Compañías**: listar, buscar por ID, crear, PUT, PATCH, DELETE
- **CRUD Empleados**: listar, buscar por ID, crear, PUT, PATCH, DELETE
- **Modal Bulk contextual** (`openBulkModal` + `submitBulkCarga`):
  - En pestaña **Compañías** → llama a `POST /api/companias/con-empleados` (transaccional)
  - En pestaña **Empleados** → llama a `POST /api/empleados/bulk` (carga masiva)
- **Consola HTTP en vivo**: muestra cada petición y respuesta en tiempo real
- **Toasts**: mensajes de éxito/error/advertencia con auto-cierre
- **Loader global**: overlay animado durante peticiones

---

## 🎨 Sistema de Diseño (`styles.css`)

| Token | Valor |
|-------|-------|
| `--bg-dark` | `#07080f` |
| `--blue` | `#00d4ff` |
| `--purple` | `#8b5cf6` |
| `--green` | `#10b981` |
| `--red` | `#ef4444` |
| `--amber` | `#f59e0b` |
| `--font-ui` | Outfit (Google Fonts) |
| `--font-body` | Plus Jakarta Sans |
| `--font-mono` | Consolas / Monaco |

Componentes implementados: Navbar, Glass Cards, Tablas responsive, Botones, Badges, Tabs, Modal (normal / lg / sm), Toasts, Loader, Consola HTTP, Formularios, Responsive breakpoints.

---

## 🔑 Pantalla de Login (`login.html`)

- Formulario con correo + contraseña
- Panel lateral con **Acceso Rápido**: tarjetas pre-configuradas para Medellín y Bogotá
- Al hacer clic en una tarjeta se autocompletan las credenciales y se envía el formulario
- Redirige automáticamente al dashboard si ya hay sesión activa
- Banner de error animado con animación `shake`

---

## 🏠 Dashboard (`index.html`)

### HUD Superior
- **Tarjeta de Perfil**: avatar generado con iniciales, correo, rol y badge de ciudad coloreado
- **Tarjeta de Política**: muestra qué operaciones puede/no puede hacer el usuario actual

### Panel CRUD
- **Tab Compañías**: tabla con ID, Nombre, Dirección, Teléfono y acciones por fila (Ver, Editar PUT, Editar PATCH, Eliminar)
- **Tab Empleados**: tabla con ID, Nombre, Correo, Cargo, Salario, Compañía y acciones
- Barra de búsqueda en tiempo real + búsqueda por ID exacto
- Toolbar con botones: Registrar, Bulk (contextual), DELETE masivo

### Modal Bulk — Comportamiento Contextual
| Pestaña activa | Título del modal | Endpoint llamado | Payload esperado |
|---------------|-----------------|-----------------|-----------------|
| Compañías | "Crear Compañía con Empleados (Transaccional)" | `POST /api/companias/con-empleados` | `{ nombre, direccion, telefono, empleados: [...] }` |
| Empleados | "Carga Masiva de Empleados (POST Bulk)" | `POST /api/empleados/bulk` | `[{ nombre, apellido, correo, cargo, salario, compania_id }, ...]` |

### Modales de Formularios
- **Crear / PUT Compañía**: formulario completo (`cia-modal`)
- **PATCH Compañía**: solo los campos opcionales que se quieran cambiar (`patch-cia-modal`)
- **Crear / PUT Empleado**: formulario completo con selector de compañía (`emp-modal`)
- **PATCH Empleado**: campos opcionales (`patch-emp-modal`)
- **Ver por ID**: muestra el JSON completo del registro (`detail-modal`)
- **Confirmar DELETE**: modal de confirmación antes de eliminar (`confirm-modal`)

### Consola HTTP en Vivo
Panel inferior que muestra en tiempo real cada petición y respuesta de la API, incluyendo método, URL, status code y preview del payload.

---

## 🔗 Integración con el Backend

Django sirve el frontend directamente gracias a la configuración en `backend/config/settings.py`:

```python
TEMPLATES = [{ 'DIRS': [BASE_DIR.parent / 'frontend'] }]
STATICFILES_DIRS = [BASE_DIR.parent / 'frontend']
```

Y en `backend/config/urls.py`:
```python
path('', TemplateView.as_view(template_name='index.html')),
path('login', TemplateView.as_view(template_name='login.html')),
```

Los archivos JS y CSS se sirven con la URL `/static/css/styles.css` y `/static/js/*.js`.
