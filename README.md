# CompanyEmployees01 — SENA ADSO Academic Project

Este repositorio contiene las actividades y proyectos de la formación **ADSO del SENA** para el módulo de desarrollo de APIs REST empresariales.

El repositorio cuenta con dos implementaciones completas del sistema de administración de Compañías y Empleados, diseñadas bajo estándares arquitectónicos modernos y separación estricta de capas:

---

## 📁 Estructura del Repositorio

### 1. ⚙️ [CompanyEmployees01 (ASP.NET Core Web API)](file:///c:/Users/PC/OneDrive/Documentos/adso-3278641-4t/CompanyEmployees01/CompanyEmployees01)
Implementación original utilizando el ecosistema de **.NET 8 / C#**:
- **Patrón:** Controller-Service-Repository.
- **Logger:** Logger personalizado con Serilog.
- **Estado:** Activo/Base original.

---

### 2. 🐍 [company_employees_django (Python + Django REST Framework)](file:///c:/Users/PC/OneDrive/Documentos/adso-3278641-4t/CompanyEmployees01/company_employees_django)
Nueva implementación transferida como actividad académica obligatoria, aplicando de forma estricta:
- **Arquitectura:** Arquitectura de Cebolla (Onion Architecture).
- **Patrón de Persistencia:** Repository Pattern (sin commits en repositorios).
- **Control Transaccional:** Unit of Work usando `transaction.atomic` de Django.
- **Lógica de Negocio:** Service Layer (toda lógica de negocio vive en servicios).
- **Endpoints:** CRUD completo para Compañías y Empleados (12 endpoints HTTP en total).
- **Transacción Atómica:** `POST /api/companias/con-empleados` con rollback total ante fallos.
- **Logging de Transacciones:** Archivo estructurado `logs/app.log` que registra de forma detallada cada transacción, inicio, commit y rollback.
- **Pruebas Automatizadas:** Suite de pruebas bajo `python manage.py test`.

---

## 🚀 Cómo Empezar con el Proyecto Django

1. Diríjase a la carpeta del proyecto:
   ```powershell
   cd company_employees_django
   ```
2. Instale los requerimientos:
   ```powershell
   pip install -r requirements.txt
   ```
3. Ejecute las migraciones y cree la base de datos SQLite:
   ```powershell
   python manage.py makemigrations database
   python manage.py migrate
   ```
4. Poblar datos iniciales de prueba (Seed Data):
   ```powershell
   python manage.py seed
   ```
5. Ejecutar la suite de pruebas:
   ```powershell
   python manage.py test
   ```
6. Iniciar el servidor local:
   ```powershell
   python manage.py runserver
   ```

Para más detalles acerca de la arquitectura de la API de Django, consulte el [README de Django](file:///c:/Users/PC/OneDrive/Documentos/adso-3278641-4t/CompanyEmployees01/company_employees_django/README.md).