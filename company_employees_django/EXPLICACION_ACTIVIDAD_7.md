# 📖 Guía Explicativa — Actividad 7
## ¿Qué hicimos y para qué sirve?
### (Explicado para alguien que no sabe programación)

---

## 🌐 ¿Qué es esta aplicación?

Imagina que tienes una empresa y necesitas llevar el registro de todas tus **compañías** y sus **empleados**. Esta aplicación es como un cuaderno digital donde puedes:

- 📋 **Ver** la lista de todas las compañías y empleados
- ➕ **Agregar** nuevas compañías y empleados
- ✏️ **Editar** la información de los que ya existen
- 🗑️ **Eliminar** los que ya no necesites

Todo esto se hace desde una **página web** que se abre en tu navegador de internet, igual que cuando entras a Facebook o a tu correo.

---

## 🏗️ ¿Cómo está construida?

La aplicación tiene **dos partes principales**, como una casa con habitaciones separadas:

### 🖥️ El Backend (la "cocina")
Es la parte que **no se ve** pero hace todo el trabajo pesado:
- Guarda la información en una base de datos (como una hoja de Excel muy avanzada)
- Se asegura de que los datos sean correctos (que los correos tengan @, que los salarios sean positivos, etc.)
- Controla quién puede hacer qué, según su ciudad

### 🎨 El Frontend (la "sala")
Es la parte que **sí se ve** en el navegador:
- La pantalla de inicio de sesión
- El panel de control con las tablas de compañías y empleados
- Los formularios para crear o editar registros
- Los botones que aparecen o desaparecen según los permisos del usuario

---

## 🔐 ¿Cómo funciona el inicio de sesión?

Cuando entras a la aplicación, lo primero que ves es una **pantalla de login** (inicio de sesión). Es como la portería de un edificio: sin identificarte, no puedes entrar.

1. Escribes tu **correo** y **contraseña**
2. El sistema verifica que seas quien dices ser
3. Si es correcto, te entrega un **"carnet digital"** llamado **JWT Token** (una cadena larga de letras y números)
4. Este carnet queda guardado en tu navegador y se envía automáticamente en cada acción que haces, sin que tengas que escribirlo de nuevo
5. Si el carnet es falso o está vencido, el sistema te rechaza y te pide que inicies sesión nuevamente

---

## 🏙️ ¿Por qué importa la ciudad del usuario?

Aquí está la parte más especial de esta actividad. El sistema tiene **reglas diferentes** según la ciudad donde trabaja el administrador:

### 👷 Usuario de Medellín puede:
- ✅ Ver todos los registros
- ✅ Agregar nuevos registros
- ✅ Cargar muchos registros a la vez (carga masiva)
- ✅ **Eliminar** registros
- ❌ **NO puede** editar (no puede usar las funciones de edición completa o parcial)

### 🏢 Usuario de Bogotá puede:
- ✅ Ver todos los registros
- ✅ Agregar nuevos registros
- ✅ Cargar muchos registros a la vez
- ✅ **Editar** registros (tanto edición completa como parcial)
- ❌ **NO puede** eliminar registros

La aplicación **detecta automáticamente** la ciudad del usuario cuando inicia sesión y **oculta o bloquea** los botones que no le corresponden. Si de todas formas intenta hacer algo que no puede, aparece un mensaje explicándole por qué no está permitido.

---

## 📋 ¿Qué cosas puedo hacer en el panel principal?

Una vez que inicias sesión, entras al **Dashboard** (panel de control). Tiene dos secciones principales:

### 🏢 Pestaña de Compañías
Puedes ver la lista de todas las empresas registradas. Para cada empresa puedes (según tus permisos):
- 👁️ **Ver el detalle** — ver toda la información de esa empresa en un cuadro emergente
- ✏️ **Editar completo** (solo Bogotá) — cambiar todos los datos de la empresa
- 🔧 **Editar parcial** (solo Bogotá) — cambiar solo un dato específico, como el teléfono, sin tocar los demás
- 🗑️ **Eliminar** (solo Medellín) — borrar la empresa del sistema

### 👥 Pestaña de Empleados
Lo mismo pero para empleados. Puedes ver su nombre, correo, cargo, salario y a qué empresa pertenece.

---

## ⚡ ¿Qué es la "Carga Masiva"?

Imagina que necesitas agregar 50 empleados de una sola vez. Sería muy lento hacerlo uno por uno. La **carga masiva** te permite escribir todos los datos en un formato especial (llamado JSON) y subirlos todos al mismo tiempo con un solo clic.

El botón **"Bulk"** abre una ventana donde puedes pegar esa lista y ejecutar la carga completa.

---

## 🔀 ¿Qué es la operación "Transaccional"?

Esta es la parte más avanzada y más importante de la actividad.

Imagina que vas a crear una empresa nueva con 5 empleados al mismo tiempo. El proceso funciona así:

1. ✅ Se crea la empresa
2. ✅ Se crea el empleado 1
3. ✅ Se crea el empleado 2
4. ✅ Se crea el empleado 3
5. ✅ Se crea el empleado 4
6. ❌ El empleado 5 tiene un correo repetido → ¡Error!

¿Qué debería pasar? Si el sistema no fuera "transaccional", quedarían guardados la empresa y los 4 primeros empleados, y habría que limpiar a mano. **Con la operación transaccional**, si CUALQUIER cosa falla, TODO se cancela automáticamente — como si nunca hubiera pasado. Esto garantiza que los datos siempre queden consistentes.

Esto se logra con el **endpoint `POST /api/companias/con-empleados`**: en el panel, cuando estás en la pestaña de Compañías y presionas "Bulk", el formulario te pide crear la empresa y sus empleados juntos, en esta misma operación segura.

---

## 📡 ¿Qué es la "Consola HTTP en vivo"?

En la parte inferior del dashboard hay una ventana pequeña que muestra, en tiempo real, todas las peticiones que hace el navegador al servidor. Es como ver "entre bastidores" lo que está pasando:

- Muestra si una petición fue exitosa (✅ verde) o falló (❌ rojo)
- Muestra el tipo de operación (GET para consultar, POST para crear, PUT/PATCH para editar, DELETE para eliminar)
- Es muy útil para entender qué está pasando y para hacer pruebas

---

## 🏛️ ¿Por qué esta arquitectura se llama "Onion" (Cebolla)?

El código del backend está organizado en capas, como las capas de una cebolla:

```
     ┌─────────────────┐
     │  API / Web      │  ← Lo que ve el navegador
     │  ┌───────────┐  │
     │  │Application│  │  ← La lógica del negocio
     │  │ ┌───────┐ │  │
     │  │ │Domain │ │  │  ← Las reglas más puras
     │  │ └───────┘ │  │
     │  └───────────┘  │
     └─────────────────┘
       Infrastructure    ← La base de datos y seguridad
```

**¿Para qué sirve esto?** Para que si en el futuro quieres cambiar la base de datos (de SQLite a PostgreSQL, por ejemplo), solo tienes que cambiar la capa de "infraestructura" sin tocar las reglas de negocio ni la interfaz web. El código queda limpio, ordenado y fácil de mantener.

---

## 🗃️ ¿Cómo se guarda la información?

La información se guarda en una **base de datos SQLite**. Es un archivo en el computador (llamado `db.sqlite3`) que funciona como una tabla de Excel gigante con varias hojas:

- Hoja "Compañías": nombre, dirección, teléfono, fecha de creación
- Hoja "Empleados": nombre, apellido, correo, cargo, salario, a qué compañía pertenece
- Hoja "Usuarios": correo, contraseña cifrada, rol, ciudad

---

## 🧪 Datos de Prueba que se crearon automáticamente

Al instalar el sistema, se corrió un comando (`python manage.py seed`) que creó automáticamente:

**Compañías:**
- TechCorp Colombia (Bogotá)
- Innovación Digital SAS (Medellín)
- SoftDev Solutions (Cali)

**Usuarios de prueba:**

| Correo | Contraseña | Ciudad | Lo que puede hacer |
|--------|-----------|--------|--------------------|
| admin_medellin@sena.edu.co | Admin123! | Medellín | Todo menos editar |
| admin_bogota@sena.edu.co | Admin123! | Bogotá | Todo menos eliminar |
| usuario@techcorp.co | Usuario123! | Medellín | Solo su empresa |

---

## ✅ Resumen: ¿Todo lo que se pedía fue implementado?

| Requerimiento | Estado |
|---------------|:------:|
| Pantalla de Login | ✅ |
| Consumir endpoint de autenticación | ✅ |
| Guardar token en LocalStorage | ✅ |
| Redirigir al Dashboard después de login | ✅ |
| Mostrar nombre y ciudad en la interfaz | ✅ |
| Protección de rutas sin token | ✅ |
| Token Bearer automático en peticiones | ✅ |
| Listar todos los registros (compañías y empleados) | ✅ |
| Buscar registro por ID | ✅ |
| Crear registro (POST) | ✅ |
| Carga masiva mediante textarea JSON | ✅ |
| Actualizar registro completo (PUT) — solo Bogotá | ✅ |
| Actualizar registro parcial (PATCH) — solo Bogotá | ✅ |
| Eliminar registro (DELETE) — solo Medellín | ✅ |
| Endpoint transaccional compañía + empleados | ✅ |
| Diseño moderno y responsive | ✅ |
| Navbar superior | ✅ |
| Tabla responsive | ✅ |
| Formularios organizados | ✅ |
| Mensajes de éxito y error (toasts) | ✅ |
| Loader mientras se procesan peticiones | ✅ |
| Botón de cerrar sesión | ✅ |
| Ocultar/deshabilitar PUT y PATCH para Medellín | ✅ |
| Ocultar/deshabilitar DELETE para Bogotá | ✅ |
| Mensajes claros cuando se intenta acción no permitida | ✅ |

---

*Proyecto desarrollado para el SENA — ADSO 3278641 — Actividad 7*
