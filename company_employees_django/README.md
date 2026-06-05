# Enterprise Hub — Gestión de Compañías y Empleados

Sistema completo de administración corporativa con **Onion Architecture**, **JWT con control de acceso por ciudad**, operaciones transaccionales y una interfaz web moderna con permisos dinámicos por usuario.

---

## 📂 Estructura del Proyecto

```text
├── backend/                    # API REST (Django + DRF) — Onion Architecture
│   ├── api/                    # Controladores, Serializers, Permisos
│   ├── application/            # Servicios y lógica de negocio
│   ├── domain/                 # Entidades puras e interfaces (núcleo)
│   ├── infrastructure/         # ORM, JWT, Repositorios, Seed
│   ├── tests/                  # Suite de pruebas automatizadas
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                   # Interfaz web SPA (HTML + CSS + JS Vanilla)
│   ├── login.html              # Pantalla de inicio de sesión con JWT
│   ├── index.html              # Dashboard principal CRUD
│   ├── css/
│   │   └── styles.css          # Sistema de diseño dark-mode glassmorphism
│   └── js/
│       ├── storage.js          # Gestión de sesión (LocalStorage)
│       ├── auth.js             # Login / logout / protección de rutas
│       ├── permissions.js      # Reglas de permisos por ciudad
│       ├── api.js              # Cliente HTTP centralizado (Bearer Token)
│       └── dashboard.js        # Lógica CRUD + modales + consola HTTP
│
├── README.md                   # Este archivo
└── README_PARTE_II.md          # Documentación técnica extendida (módulos 7-12)
```

---

## 🚀 Inicio Rápido

### 1. Preparar el Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed        # Crea usuarios y datos de prueba
python manage.py runserver
```

### 2. Abrir la interfaz

Navega a **[http://127.0.0.1:8000](http://127.0.0.1:8000)** — Django sirve el frontend automáticamente.

---

## 👤 Usuarios de Prueba

| Correo | Contraseña | Ciudad | Permisos |
|--------|------------|--------|----------|
| `admin_medellin@sena.edu.co` | `Admin123!` | Medellín | GET, POST, BULK, DELETE — **sin PUT/PATCH** |
| `admin_bogota@sena.edu.co` | `Admin123!` | Bogotá | GET, POST, BULK, PUT, PATCH — **sin DELETE** |
| `admin@sena.edu.co` | `Admin123!` | Medellín | Igual que Medellín |
| `usuario@techcorp.co` | `Usuario123!` | Medellín | Solo empleados de su compañía |

---

## 🔗 Endpoints Principales

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/auth/registro` | Registrar nuevo usuario |
| `POST` | `/api/auth/login` | Iniciar sesión — devuelve token JWT |
| `GET` | `/api/auth/perfil` | Datos del usuario autenticado |

### Compañías
| Método | Ruta | Permisos |
|--------|------|----------|
| `GET` | `/api/companias` | Todos los autenticados |
| `GET` | `/api/companias/{id}` | Todos los autenticados |
| `POST` | `/api/companias` | ADMIN o USUARIO |
| `PUT` | `/api/companias/{id}` | Solo Bogotá |
| `PATCH` | `/api/companias/{id}` | Solo Bogotá |
| `DELETE` | `/api/companias/{id}` | Solo Medellín |
| `POST` | `/api/companias/con-empleados` | ADMIN — Transaccional |

### Empleados
| Método | Ruta | Permisos |
|--------|------|----------|
| `GET` | `/api/empleados` | Todos los autenticados |
| `GET` | `/api/empleados/{id}` | Todos los autenticados |
| `POST` | `/api/empleados` | ADMIN o USUARIO |
| `PUT` | `/api/empleados/{id}` | Solo Bogotá |
| `PATCH` | `/api/empleados/{id}` | Solo Bogotá |
| `DELETE` | `/api/empleados/{id}` | Solo Medellín |
| `POST` | `/api/empleados/bulk` | ADMIN o USUARIO — Carga masiva |
| `DELETE` | `/api/empleados/bulk-delete` | Solo Medellín |

---

## 🧪 Pruebas Automatizadas

```bash
cd backend
python manage.py test
```

---

## 📖 Documentación Adicional

- [Backend — Onion Architecture](backend/README.md)
- [Frontend — SPA y módulos JS](frontend/README.md)
- [Módulos 7-12 (CRUD Masivo, JWT, Políticas, Tests)](README_PARTE_II.md)
