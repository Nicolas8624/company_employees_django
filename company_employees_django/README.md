# API REST Compañías y Empleados — Django & Onion Architecture

Este proyecto es una implementación de una **API REST** para administrar compañías y empleados utilizando **Python con Django y Django REST Framework (DRF)**. Ha sido diseñado siguiendo estrictamente **Onion Architecture**, **Repository Pattern**, **Unit of Work** y buenas prácticas de desarrollo empresarial para cumplir con las directrices de la actividad académica del SENA.

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.12+
- **Framework Web:** Django 6.0+
- **REST Framework:** Django REST Framework (DRF) 3.15+
- **ORM:** Django ORM
- **Base de Datos:** SQLite
- **Manejo Transaccional:** `transaction.atomic` de Django
- **Logging:** Módulo `logging` nativo de Python

---

## 🧅 Onion Architecture (Arquitectura de Cebolla)

La arquitectura del proyecto está estructurada en capas concéntricas, donde las dependencias siempre apuntan hacia el interior (el Dominio):

```
company_employees_django/
├── domain/              # CAPA 1: Core / Núcleo de la aplicación (Sin dependencias externas)
│   ├── entities/        # Entidades puras de negocio (dataclasses)
│   └── interfaces/      # Contratos de repositorios y Unit of Work (ABCs)
│
├── application/         # CAPA 2: Lógica de negocio (Depende únicamente de Domain)
│   ├── services/        # Orquestación de casos de uso empresariales
│   └── dtos/            # Mapeo de datos para transferencia segura
│
├── infrastructure/      # CAPA 3: Implementación técnica y persistencia (Acceso al ORM)
│   ├── database/        # Modelos de Django ORM y migraciones
│   ├── repositories/    # Implementación concreta de IRepository (sin realizar commits)
│   ├── unit_of_work/    # Implementación concreta de IUnitOfWork (controlador transaccional)
│   └── seed/            # Poblamiento inicial de datos
│
└── api/                 # CAPA 4: Interfaz HTTP / Entrada de la aplicación (Depende de Application)
    ├── controllers/     # APIViews que reciben peticiones HTTP y delegan al Service
    ├── serializers/     # Validadores y serializadores de DRF
    ├── routes/          # Mapeo de endpoints de la aplicación
    └── middlewares/     # Captura y logging de excepciones globales
```

### 🔄 Flujo de Ejecución Obligatorio
El flujo de datos sigue de forma estricta la siguiente secuencia:
$$\text{Controller} \longrightarrow \text{Service} \longrightarrow \text{UnitOfWork} \longrightarrow \text{Repository} \longrightarrow \text{ORM} \longrightarrow \text{Database}$$

- **Los controladores NO acceden al ORM ni a los modelos directamente.** Delegar al `Service`.
- **Los repositorios NO realizan commits.** El `UnitOfWork` es el único responsable de abrir la transacción, consolidar (`commit`) y revertir (`rollback`).

---

## 🚀 Instalación y Uso de la Aplicación

Siga los siguientes pasos para iniciar el proyecto localmente en su sistema Windows:

### 1. Clonar e Instalar Dependencias
Asegúrese de encontrarse dentro del directorio del proyecto Django:
```powershell
# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar Migraciones de la Base de Datos
Cree las tablas correspondientes a los modelos ORM de Compañías y Empleados en SQLite:
```powershell
python manage.py makemigrations database
python manage.py migrate
```

### 3. Poblar la Base de Datos con Datos de Prueba (Seed Data)
Se ha creado un comando de management personalizado que creará compañías y empleados iniciales para pruebas:
```powershell
python manage.py seed
```

### 4. Iniciar el Servidor de Desarrollo
```powershell
python manage.py runserver
```
La API estará disponible en `http://127.0.0.1:8000/`.

---

## 📌 Catálogo de Endpoints

### 🏢 Compañías
- **Listar Compañías:** `GET /api/companias`
- **Detalle de Compañía:** `GET /api/companias/{id}`
- **Crear Compañía:** `POST /api/companias`
- **Actualizar Compañía:** `PUT /api/companias/{id}`
- **Eliminar Compañía:** `DELETE /api/companias/{id}`
- **Empleados por Compañía:** `GET /api/companias/{id}/empleados`

### 👥 Empleados
- **Listar Empleados:** `GET /api/empleados`
- **Detalle de Empleado:** `GET /api/empleados/{id}`
- **Crear Empleado:** `POST /api/empleados`
- **Actualizar Empleado:** `PUT /api/empleados/{id}`
- **Eliminar Empleado:** `DELETE /api/empleados/{id}`

### ⚡ Endpoint Transaccional Obligatorio
- **Creación Conjunta:** `POST /api/companias/con-empleados`
  - Permite crear una compañía junto con una lista de múltiples empleados en una única operación atómica.
  - **Mecanismo de Rollback:** Si falla la creación de cualquier empleado (por ejemplo, validación de salario inválido o formato de correo erróneo), se ejecuta un rollback completo del bloque de base de datos; asegurando que ni la compañía ni los empleados parciales queden guardados en la BD.

Ejemplo de payload para `POST /api/companias/con-empleados`:
```json
{
  "nombre": "SENA Software Factory",
  "direccion": "Calle de la Tecnología 45",
  "telefono": "+57 601 327-8641",
  "empleados": [
    {
      "nombre": "Diana",
      "apellido": "Gomez",
      "correo": "diana.gomez@sena.edu.co",
      "cargo": "Líder de Desarrollo",
      "salario": 9500000.00
    },
    {
      "nombre": "Andrés",
      "apellido": "Rincón",
      "correo": "andres.rincon@sena.edu.co",
      "cargo": "Desarrollador Junior",
      "salario": 3500000.00
    }
  ]
}
```

---

## 📝 Sistema de Logging e Historial de Transacciones

Todos los sucesos del sistema se registran en la consola y en el archivo de registro `logs/app.log` utilizando un formateador estructurado que indica la fecha, nivel, módulo y mensaje del suceso.

El logging captura:
- Inicio de la aplicación
- Consultas globales y por ID
- Transacciones de creación, actualización y eliminación
- **Inicio de Transacción, Commits y Rollbacks** detallados del `UnitOfWork`
- Errores de base de datos y excepciones inesperadas

Ejemplo del flujo de logs generado por el Unit of Work en una creación exitosa:
```
[2026-05-23 08:07:13] INFO api.controllers.compania_controller | POST /api/companias/con-empleados — TRANSACCIONAL
[2026-05-23 08:07:13] INFO application.services.compania_service | === INICIO TRANSACIÓN: Crear compañía con empleados ===
[2026-05-23 08:07:13] INFO infrastructure.unit_of_work.unit_of_work | UnitOfWork: Iniciando transacción
[2026-05-23 08:07:13] INFO application.services.compania_service | Compañía creada en transacción: ID=6
[2026-05-23 08:07:13] INFO application.services.compania_service | Empleado creado en transacción: ID=10, nombre=Jose Gomez
[2026-05-23 08:07:13] INFO infrastructure.unit_of_work.unit_of_work | UnitOfWork: COMMIT — Transacción confirmada exitosamente
[2026-05-23 08:07:13] INFO application.services.compania_service | === COMMIT EXITOSO: Compañía + 2 empleados ===
```

Y en un escenario con rollback automático por violación de restricciones o datos erróneos:
```
[2026-05-23 08:08:45] INFO application.services.compania_service | === INICIO TRANSACIÓN: Crear compañía con empleados ===
[2026-05-23 08:08:45] INFO infrastructure.unit_of_work.unit_of_work | UnitOfWork: Iniciando transacción
[2026-05-23 08:08:45] ERROR application.services.compania_service | === ROLLBACK: Error en transacción — NOT NULL constraint failed: empleados.salario ===
[2026-05-23 08:08:45] ERROR infrastructure.unit_of_work.unit_of_work | UnitOfWork: ROLLBACK — Error tipo=IntegrityError, mensaje=NOT NULL constraint failed: empleados.salario
```

---

## 🧪 Pruebas Automatizadas

El proyecto incluye un conjunto de pruebas automatizadas que verifican la separación de capas, la inyección del repositorio y el comportamiento de las transacciones (incluido el rollback automático de base de datos).

Para ejecutar las pruebas:
```powershell
python manage.py test
```
