/**
 * dashboard.js — Lógica principal del Dashboard
 *
 * Orquesta todas las vistas del panel de control:
 *   - Inicialización y verificación de sesión
 *   - Renderizado del perfil de usuario con ciudad y permisos
 *   - Tabs: Compañías y Empleados
 *   - CRUD completo respetando las políticas de Permissions
 *   - Logger de consola HTTP en vivo
 *   - Modales de creación/edición
 *   - Bulk create mediante textarea JSON
 *   - Buscar por ID
 */

/* =========================================================
   ESTADO GLOBAL DEL DASHBOARD
   ========================================================= */
let _user = null;          // Usuario autenticado
let _activeTab = 'companias';
let _companies = [];       // Cache de compañías para el select de empleados

/* =========================================================
   INICIALIZACIÓN
   ========================================================= */
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Proteger ruta — redirige si no hay token
    Auth.requireAuth();

    // 2. Mostrar loader mientras verificamos sesión
    showLoader(true);

    // 3. Verificar token con la API
    _user = Storage.getUser();
    const verified = await Auth.verifySession();
    if (!verified) return; // verifySession llama logout() si falla

    _user = Storage.getUser(); // re-leer datos actualizados

    // 4. Renderizar UI con datos del usuario
    renderUserProfile();
    applyPermissionsToUI();

    // 5. Suscribirse al logger HTTP
    setupApiLogger();

    // 6. Cargar tab inicial
    switchTab('companias');

    showLoader(false);
});

/* =========================================================
   PERFIL DE USUARIO
   ========================================================= */
function renderUserProfile() {
    const city = _user.ciudad || '—';
    const role = _user.rol || '—';
    const initials = (_user.correo || 'U').substring(0, 2).toUpperCase();

    document.getElementById('user-avatar').textContent = initials;
    document.getElementById('user-email').textContent = _user.correo || '—';
    document.getElementById('user-city').textContent = city;
    document.getElementById('user-role').textContent = role;

    // Badge de ciudad con color según ciudad
    const cityBadge = document.getElementById('badge-city');
    cityBadge.textContent = city;
    if (Permissions.isBogota(_user)) {
        cityBadge.classList.add('badge-bogota');
    } else if (Permissions.isMedellin(_user)) {
        cityBadge.classList.add('badge-medellin');
    }

    // Descripción de política activa
    document.getElementById('policy-text').innerHTML =
        Permissions.getPolicyDescription(_user);
}

/* =========================================================
   APLICAR PERMISOS A LA UI
   Oculta / deshabilita botones según ciudad del usuario
   ========================================================= */
function applyPermissionsToUI() {
    const canPut    = Permissions.canPut(_user);
    const canPatch  = Permissions.canPatch(_user);
    const canDelete = Permissions.canDelete(_user);

    // Botones de la toolbar
    setButtonPermission('btn-bulk-delete-compania', canDelete);
    setButtonPermission('btn-bulk-delete-empleado', canDelete);

    // Los botones de fila se aplican al renderizar cada tabla
    // (ver renderCompaniasTable y renderEmpleadosTable)
}

/**
 * Aplica el estado habilitado/deshabilitado a un botón de toolbar.
 * Si no tiene permiso, lo deshabilita y agrega tooltip explicativo.
 */
function setButtonPermission(id, allowed, action = '') {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.disabled = !allowed;
    if (!allowed && action) {
        btn.title = Permissions.getDeniedMessage(action, _user);
    }
}

/* =========================================================
   TABS
   ========================================================= */
function switchTab(tab) {
    // Desactivar tab anterior
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-view').forEach(v => v.style.display = 'none');

    // Activar tab nueva
    _activeTab = tab;
    document.getElementById(`tab-btn-${tab}`).classList.add('active');
    document.getElementById(`view-${tab}`).style.display = 'block';

    if (tab === 'companias') loadCompanias();
    if (tab === 'empleados') loadEmpleados();
}

/* =========================================================
   LOADER GLOBAL
   ========================================================= */
function showLoader(show) {
    document.getElementById('global-loader').style.display = show ? 'flex' : 'none';
}

/* =========================================================
   NOTIFICACIONES TOAST
   ========================================================= */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'fa-circle-check'
                : type === 'error'   ? 'fa-circle-xmark'
                : 'fa-circle-info';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i><span>${message}</span>`;
    container.appendChild(toast);

    // Auto-remover después de 4 segundos
    setTimeout(() => {
        toast.classList.add('toast-hide');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

/* =========================================================
   LOGGER HTTP (consola en vivo)
   ========================================================= */
function setupApiLogger() {
    window.addEventListener('api:request', (e) => {
        const { method, url, body } = e.detail;
        const payload = body ? ` → ${JSON.stringify(body).substring(0, 80)}` : '';
        addLogEntry(`[REQ] <span class="log-method">${method}</span> ${url}${payload}`, 'request');
    });

    window.addEventListener('api:response', (e) => {
        const { method, url, status, data, error } = e.detail;
        if (error) {
            addLogEntry(`[ERR] ${method} ${url} — Error de red: ${error}`, 'error');
            return;
        }
        const type = status >= 200 && status < 300 ? 'success' : 'error';
        const preview = data ? JSON.stringify(data).substring(0, 120) : 'sin datos';
        addLogEntry(`[RES] <span class="log-status-${type}">${status}</span> ${preview}`, type);
    });
}

function addLogEntry(html, type = 'info') {
    const box = document.getElementById('console-output');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.innerHTML = `<span class="log-ts">${new Date().toLocaleTimeString()}</span> ${html}`;
    box.appendChild(entry);
    box.scrollTop = box.scrollHeight;
}

function clearConsole() {
    document.getElementById('console-output').innerHTML =
        '<div class="log-entry" style="color:#6b7280;font-style:italic">Consola limpiada.</div>';
}

/* =========================================================
   ===================== COMPAÑÍAS =========================
   ========================================================= */

async function loadCompanias() {
    showLoader(true);
    const buscar = document.getElementById('search-companias').value || '';
    const result = await Api.getCompanias(1, 50, buscar);
    showLoader(false);

    if (!result.ok) {
        showToast('Error al cargar compañías: ' + (result.data?.mensaje || result.status), 'error');
        return;
    }

    _companies = result.data?.datos || result.data || [];
    renderCompaniasTable(_companies);

    // Actualizar selector de compañía en el modal de empleado
    const sel = document.getElementById('emp-compania');
    sel.innerHTML = _companies.map(c =>
        `<option value="${c.id}">${c.nombre}</option>`
    ).join('');
}

function renderCompaniasTable(list) {
    const tbody = document.getElementById('companias-tbody');
    if (!list || list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-row">
            <i class="fa-solid fa-inbox"></i><br>No hay compañías registradas
        </td></tr>`;
        return;
    }

    const canPut    = Permissions.canPut(_user);
    const canPatch  = Permissions.canPatch(_user);
    const canDelete = Permissions.canDelete(_user);

    tbody.innerHTML = list.map(c => `
        <tr>
            <td><span class="id-badge">#${c.id}</span></td>
            <td class="td-name">${c.nombre}</td>
            <td>${c.direccion}</td>
            <td>${c.telefono}</td>
            <td>
                <div class="row-actions">
                    <button class="btn-icon btn-view"
                        title="Ver por ID" onclick="verCompaniaById(${c.id})">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    <button class="btn-icon btn-edit" ${!canPut ? 'disabled title="' + Permissions.getDeniedMessage('PUT', _user) + '"' : ''}
                        onclick="${canPut ? `openEditCompaniaModal(${c.id})` : `showToast('${Permissions.getDeniedMessage('PUT', _user)}','error')`}">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn-icon btn-patch" ${!canPatch ? 'disabled title="' + Permissions.getDeniedMessage('PATCH', _user) + '"' : ''}
                        onclick="${canPatch ? `openPatchCompaniaModal(${c.id})` : `showToast('${Permissions.getDeniedMessage('PATCH', _user)}','error')`}">
                        <i class="fa-solid fa-wrench"></i>
                    </button>
                    <button class="btn-icon btn-delete" ${!canDelete ? 'disabled title="' + Permissions.getDeniedMessage('DELETE', _user) + '"' : ''}
                        onclick="${canDelete ? `deleteCompania(${c.id},'${c.nombre}')` : `showToast('${Permissions.getDeniedMessage('DELETE', _user)}','error')`}">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/* Buscar compañía por ID */
async function verCompaniaById(id) {
    if (!id) id = document.getElementById('search-cia-id').value;
    if (!id) return showToast('Ingresa un ID válido', 'warning');

    showLoader(true);
    const result = await Api.getCompaniaById(id);
    showLoader(false);

    if (!result.ok) {
        showToast(`Compañía #${id} no encontrada`, 'error');
        return;
    }
    showDetailModal('Detalle de Compañía', result.data);
}

/* Crear compañía */
function openCreateCompaniaModal() {
    resetModal('cia-modal', 'cia-form');
    document.getElementById('cia-modal-title').textContent = 'Registrar Compañía';
    document.getElementById('cia-save-btn').onclick = saveNewCompania;
    document.getElementById('cia-modal').classList.add('show');
}

async function saveNewCompania() {
    const data = {
        nombre:    document.getElementById('cia-nombre').value.trim(),
        direccion: document.getElementById('cia-direccion').value.trim(),
        telefono:  document.getElementById('cia-telefono').value.trim(),
    };
    if (!data.nombre || !data.direccion || !data.telefono) {
        return showToast('Completa todos los campos', 'warning');
    }

    showLoader(true);
    const result = await Api.createCompania(data);
    showLoader(false);

    if (result.ok) {
        closeModal('cia-modal');
        showToast('Compañía creada exitosamente', 'success');
        loadCompanias();
    } else {
        showToast('Error: ' + (result.data?.mensaje || JSON.stringify(result.data)), 'error');
    }
}

/* Editar compañía (PUT) */
async function openEditCompaniaModal(id) {
    if (!Permissions.canPut(_user)) {
        return showToast(Permissions.getDeniedMessage('PUT', _user), 'error');
    }
    showLoader(true);
    const result = await Api.getCompaniaById(id);
    showLoader(false);
    if (!result.ok) return showToast('No se pudo cargar la compañía', 'error');

    const c = result.data;
    resetModal('cia-modal', 'cia-form');
    document.getElementById('cia-modal-title').textContent = `Editar Compañía #${id} (PUT)`;
    document.getElementById('cia-nombre').value    = c.nombre;
    document.getElementById('cia-direccion').value = c.direccion;
    document.getElementById('cia-telefono').value  = c.telefono;
    document.getElementById('cia-save-btn').onclick = () => updateCompania(id);
    document.getElementById('cia-modal').classList.add('show');
}

async function updateCompania(id) {
    const data = {
        nombre:    document.getElementById('cia-nombre').value.trim(),
        direccion: document.getElementById('cia-direccion').value.trim(),
        telefono:  document.getElementById('cia-telefono').value.trim(),
    };
    showLoader(true);
    const result = await Api.updateCompania(id, data);
    showLoader(false);

    if (result.ok) {
        closeModal('cia-modal');
        showToast('Compañía actualizada (PUT)', 'success');
        loadCompanias();
    } else {
        showToast('Error: ' + (result.data?.mensaje || JSON.stringify(result.data)), 'error');
    }
}

/* PATCH compañía */
async function openPatchCompaniaModal(id) {
    if (!Permissions.canPatch(_user)) {
        return showToast(Permissions.getDeniedMessage('PATCH', _user), 'error');
    }
    showLoader(true);
    const result = await Api.getCompaniaById(id);
    showLoader(false);
    if (!result.ok) return showToast('No se pudo cargar la compañía', 'error');

    const c = result.data;
    resetModal('patch-cia-modal', 'patch-cia-form');
    document.getElementById('patch-cia-modal-title').textContent = `PATCH Compañía #${id}`;
    document.getElementById('patch-cia-nombre').placeholder    = c.nombre;
    document.getElementById('patch-cia-direccion').placeholder = c.direccion;
    document.getElementById('patch-cia-telefono').placeholder  = c.telefono;
    document.getElementById('patch-cia-save-btn').onclick = () => patchCompania(id);
    document.getElementById('patch-cia-modal').classList.add('show');
}

async function patchCompania(id) {
    const data = {};
    const n = document.getElementById('patch-cia-nombre').value.trim();
    const d = document.getElementById('patch-cia-direccion').value.trim();
    const t = document.getElementById('patch-cia-telefono').value.trim();
    if (n) data.nombre    = n;
    if (d) data.direccion = d;
    if (t) data.telefono  = t;

    if (Object.keys(data).length === 0) {
        return showToast('Ingresa al menos un campo para modificar', 'warning');
    }

    showLoader(true);
    const result = await Api.patchCompania(id, data);
    showLoader(false);

    if (result.ok) {
        closeModal('patch-cia-modal');
        showToast('Compañía actualizada parcialmente (PATCH)', 'success');
        loadCompanias();
    } else {
        showToast('Error: ' + (result.data?.mensaje || JSON.stringify(result.data)), 'error');
    }
}

/* Eliminar compañía (DELETE) */
async function deleteCompania(id, nombre) {
    if (!Permissions.canDelete(_user)) {
        return showToast(Permissions.getDeniedMessage('DELETE', _user), 'error');
    }
    openConfirmModal(
        `¿Eliminar compañía <strong>${nombre}</strong>?`,
        'Esta acción no se puede deshacer.',
        async () => {
            showLoader(true);
            const result = await Api.deleteCompania(id);
            showLoader(false);
            if (result.ok || result.status === 204) {
                showToast('Compañía eliminada', 'success');
                loadCompanias();
            } else {
                showToast('Error al eliminar: ' + (result.data?.mensaje || result.status), 'error');
            }
        }
    );
}

/* =========================================================
   ===================== EMPLEADOS =========================
   ========================================================= */

async function loadEmpleados() {
    showLoader(true);
    const buscar = document.getElementById('search-empleados').value || '';
    const result = await Api.getEmpleados(1, 50, buscar);
    showLoader(false);

    if (!result.ok) {
        showToast('Error al cargar empleados: ' + (result.data?.mensaje || result.status), 'error');
        return;
    }

    const list = result.data?.datos || result.data || [];
    renderEmpleadosTable(list);
}

function renderEmpleadosTable(list) {
    const tbody = document.getElementById('empleados-tbody');
    if (!list || list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-row">
            <i class="fa-solid fa-inbox"></i><br>No hay empleados registrados
        </td></tr>`;
        return;
    }

    const canPut    = Permissions.canPut(_user);
    const canPatch  = Permissions.canPatch(_user);
    const canDelete = Permissions.canDelete(_user);

    tbody.innerHTML = list.map(e => `
        <tr>
            <td><span class="id-badge">#${e.id}</span></td>
            <td class="td-name">${e.nombre} ${e.apellido}</td>
            <td>${e.correo}</td>
            <td>${e.cargo}</td>
            <td class="td-salary">$${Number(e.salario).toLocaleString('es-CO')}</td>
            <td>${e.compania_nombre || e.compania_id}</td>
            <td>
                <div class="row-actions">
                    <button class="btn-icon btn-view"
                        title="Ver por ID" onclick="verEmpleadoById(${e.id})">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    <button class="btn-icon btn-edit" ${!canPut ? 'disabled title="' + Permissions.getDeniedMessage('PUT', _user) + '"' : ''}
                        onclick="${canPut ? `openEditEmpleadoModal(${e.id})` : `showToast('${Permissions.getDeniedMessage('PUT', _user)}','error')`}">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn-icon btn-patch" ${!canPatch ? 'disabled title="' + Permissions.getDeniedMessage('PATCH', _user) + '"' : ''}
                        onclick="${canPatch ? `openPatchEmpleadoModal(${e.id})` : `showToast('${Permissions.getDeniedMessage('PATCH', _user)}','error')`}">
                        <i class="fa-solid fa-wrench"></i>
                    </button>
                    <button class="btn-icon btn-delete" ${!canDelete ? 'disabled title="' + Permissions.getDeniedMessage('DELETE', _user) + '"' : ''}
                        onclick="${canDelete ? `deleteEmpleado(${e.id},'${e.nombre}')` : `showToast('${Permissions.getDeniedMessage('DELETE', _user)}','error')`}">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/* Ver empleado por ID */
async function verEmpleadoById(id) {
    if (!id) id = document.getElementById('search-emp-id').value;
    if (!id) return showToast('Ingresa un ID válido', 'warning');

    showLoader(true);
    const result = await Api.getEmpleadoById(id);
    showLoader(false);

    if (!result.ok) {
        showToast(`Empleado #${id} no encontrado`, 'error');
        return;
    }
    showDetailModal('Detalle de Empleado', result.data);
}

/* Crear empleado */
function openCreateEmpleadoModal() {
    resetModal('emp-modal', 'emp-form');
    document.getElementById('emp-modal-title').textContent = 'Registrar Empleado';
    document.getElementById('emp-save-btn').onclick = saveNewEmpleado;
    document.getElementById('emp-modal').classList.add('show');
}

async function saveNewEmpleado() {
    const data = {
        nombre:     document.getElementById('emp-nombre').value.trim(),
        apellido:   document.getElementById('emp-apellido').value.trim(),
        correo:     document.getElementById('emp-correo').value.trim(),
        cargo:      document.getElementById('emp-cargo').value.trim(),
        salario:    document.getElementById('emp-salario').value,
        compania_id: parseInt(document.getElementById('emp-compania').value),
    };
    if (!data.nombre || !data.apellido || !data.correo || !data.cargo || !data.salario) {
        return showToast('Completa todos los campos', 'warning');
    }

    showLoader(true);
    const result = await Api.createEmpleado(data);
    showLoader(false);

    if (result.ok) {
        closeModal('emp-modal');
        showToast('Empleado creado exitosamente', 'success');
        loadEmpleados();
    } else {
        showToast('Error: ' + (result.data?.mensaje || JSON.stringify(result.data)), 'error');
    }
}

/* Editar empleado (PUT) */
async function openEditEmpleadoModal(id) {
    if (!Permissions.canPut(_user)) {
        return showToast(Permissions.getDeniedMessage('PUT', _user), 'error');
    }
    showLoader(true);
    const result = await Api.getEmpleadoById(id);
    showLoader(false);
    if (!result.ok) return showToast('No se pudo cargar el empleado', 'error');

    const e = result.data;
    resetModal('emp-modal', 'emp-form');
    document.getElementById('emp-modal-title').textContent = `Editar Empleado #${id} (PUT)`;
    document.getElementById('emp-nombre').value   = e.nombre;
    document.getElementById('emp-apellido').value = e.apellido;
    document.getElementById('emp-correo').value   = e.correo;
    document.getElementById('emp-cargo').value    = e.cargo;
    document.getElementById('emp-salario').value  = e.salario;
    document.getElementById('emp-compania').value = e.compania_id;
    document.getElementById('emp-save-btn').onclick = () => updateEmpleado(id);
    document.getElementById('emp-modal').classList.add('show');
}

async function updateEmpleado(id) {
    const data = {
        nombre:     document.getElementById('emp-nombre').value.trim(),
        apellido:   document.getElementById('emp-apellido').value.trim(),
        correo:     document.getElementById('emp-correo').value.trim(),
        cargo:      document.getElementById('emp-cargo').value.trim(),
        salario:    document.getElementById('emp-salario').value,
        compania_id: parseInt(document.getElementById('emp-compania').value),
    };
    showLoader(true);
    const result = await Api.updateEmpleado(id, data);
    showLoader(false);

    if (result.ok) {
        closeModal('emp-modal');
        showToast('Empleado actualizado (PUT)', 'success');
        loadEmpleados();
    } else {
        showToast('Error: ' + (result.data?.mensaje || JSON.stringify(result.data)), 'error');
    }
}

/* PATCH empleado */
async function openPatchEmpleadoModal(id) {
    if (!Permissions.canPatch(_user)) {
        return showToast(Permissions.getDeniedMessage('PATCH', _user), 'error');
    }
    showLoader(true);
    const result = await Api.getEmpleadoById(id);
    showLoader(false);
    if (!result.ok) return showToast('No se pudo cargar el empleado', 'error');

    const e = result.data;
    resetModal('patch-emp-modal', 'patch-emp-form');
    document.getElementById('patch-emp-modal-title').textContent = `PATCH Empleado #${id}`;
    document.getElementById('patch-emp-nombre').placeholder   = e.nombre;
    document.getElementById('patch-emp-apellido').placeholder = e.apellido;
    document.getElementById('patch-emp-correo').placeholder   = e.correo;
    document.getElementById('patch-emp-cargo').placeholder    = e.cargo;
    document.getElementById('patch-emp-salario').placeholder  = e.salario;
    document.getElementById('patch-emp-save-btn').onclick = () => patchEmpleado(id);
    document.getElementById('patch-emp-modal').classList.add('show');
}

async function patchEmpleado(id) {
    const data = {};
    const fields = ['nombre','apellido','correo','cargo','salario'];
    fields.forEach(f => {
        const val = document.getElementById(`patch-emp-${f}`).value.trim();
        if (val) data[f] = f === 'salario' ? parseFloat(val) : val;
    });

    if (Object.keys(data).length === 0) {
        return showToast('Ingresa al menos un campo para modificar', 'warning');
    }

    showLoader(true);
    const result = await Api.patchEmpleado(id, data);
    showLoader(false);

    if (result.ok) {
        closeModal('patch-emp-modal');
        showToast('Empleado actualizado parcialmente (PATCH)', 'success');
        loadEmpleados();
    } else {
        showToast('Error: ' + (result.data?.mensaje || JSON.stringify(result.data)), 'error');
    }
}

/* DELETE empleado */
async function deleteEmpleado(id, nombre) {
    if (!Permissions.canDelete(_user)) {
        return showToast(Permissions.getDeniedMessage('DELETE', _user), 'error');
    }
    openConfirmModal(
        `¿Eliminar empleado <strong>${nombre}</strong>?`,
        'Esta acción no se puede deshacer.',
        async () => {
            showLoader(true);
            const result = await Api.deleteEmpleado(id);
            showLoader(false);
            if (result.ok || result.status === 204) {
                showToast('Empleado eliminado', 'success');
                loadEmpleados();
            } else {
                showToast('Error al eliminar: ' + (result.data?.mensaje || result.status), 'error');
            }
        }
    );
}

/* =========================================================
   BULK CREATE (carga masiva de empleados / transaccional)
   ========================================================= */
function openBulkModal() {
    resetModal('bulk-modal', null);
    const title = document.getElementById('bulk-modal-title');
    const textarea = document.getElementById('bulk-textarea');
    const hint = document.querySelector('.form-hint');

    if (_activeTab === 'companias') {
        title.innerHTML = '<i class="fa-solid fa-building" style="color:var(--blue);"></i> Crear Compañía con Empleados (Transaccional)';
        textarea.value = JSON.stringify({
            "nombre": "Nueva Compañía Transaccional",
            "direccion": "Avenida Siempre Viva 123",
            "telefono": "+57 601 555-0199",
            "empleados": [
                {
                    "nombre": "Pedro",
                    "apellido": "Pérez",
                    "correo": "pedro.perez@compania.com",
                    "cargo": "Desarrollador Junior",
                    "salario": 3500000.00
                },
                {
                    "nombre": "Marta",
                    "apellido": "Gómez",
                    "correo": "marta.gomez@compania.com",
                    "cargo": "Analista QA",
                    "salario": 4000000.00
                }
            ]
        }, null, 2);
        hint.innerHTML = '<i class="fa-solid fa-lightbulb" style="color:var(--amber);"></i> Transaccional: Se creará la compañía y todos los empleados listados. Si uno falla, se cancela todo.';
    } else {
        title.innerHTML = '<i class="fa-solid fa-users" style="color:var(--green);"></i> Carga Masiva de Empleados (POST Bulk)';
        textarea.value = JSON.stringify([
            {
                "nombre": "Ana",
                "apellido": "López",
                "correo": "ana.lopez@ejemplo.com",
                "cargo": "Desarrolladora",
                "salario": 3500000,
                "compania_id": _companies[0]?.id || 1
            }
        ], null, 2);
        hint.innerHTML = '<i class="fa-solid fa-lightbulb" style="color:var(--amber);"></i> Carga masiva: Se insertará la lista de empleados asociada a compañías existentes.';
    }
    document.getElementById('bulk-modal').classList.add('show');
}

async function submitBulkCarga() {
    let payload;
    try {
        payload = JSON.parse(document.getElementById('bulk-textarea').value);
    } catch (e) {
        return showToast('JSON inválido: ' + e.message, 'error');
    }

    showLoader(true);
    let result;
    if (_activeTab === 'companias') {
        result = await Api.createCompaniaConEmpleados(payload);
    } else {
        if (!Array.isArray(payload)) {
            showLoader(false);
            return showToast('El payload para carga masiva de empleados debe ser un array JSON', 'error');
        }
        result = await Api.bulkCreateEmpleados(payload);
    }
    showLoader(false);

    if (result.ok) {
        closeModal('bulk-modal');
        if (_activeTab === 'companias') {
            showToast('Compañía y empleados creados transaccionalmente', 'success');
            loadCompanias();
        } else {
            showToast(`${result.data?.length || payload.length} empleados creados exitosamente`, 'success');
            loadEmpleados();
        }
    } else {
        let errMsg = '';
        if (result.data?.errores) {
            errMsg = Array.isArray(result.data.errores) ? result.data.errores.join(', ') : JSON.stringify(result.data.errores);
        } else {
            errMsg = result.data?.mensaje || result.data?.detail || result.data?.error || JSON.stringify(result.data);
        }
        showToast('Error en la carga: ' + errMsg, 'error');
    }
}

/* =========================================================
   MODAL HELPERS
   ========================================================= */
function resetModal(modalId, formId) {
    if (formId) {
        const form = document.getElementById(formId);
        if (form) form.reset();
    }
}

function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}

/* Modal de detalle (GET BY ID) */
function showDetailModal(title, data) {
    document.getElementById('detail-modal-title').textContent = title;
    document.getElementById('detail-modal-body').innerHTML =
        `<pre class="detail-pre">${JSON.stringify(data, null, 2)}</pre>`;
    document.getElementById('detail-modal').classList.add('show');
}

/* Modal de confirmación (antes de DELETE) */
function openConfirmModal(titleHtml, subtitleText, onConfirm) {
    document.getElementById('confirm-title').innerHTML = titleHtml;
    document.getElementById('confirm-subtitle').textContent = subtitleText;
    document.getElementById('confirm-ok-btn').onclick = () => {
        closeModal('confirm-modal');
        onConfirm();
    };
    document.getElementById('confirm-modal').classList.add('show');
}

// Cerrar modales haciendo click fuera
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
});
