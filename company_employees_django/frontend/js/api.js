/**
 * api.js — Capa de comunicación con la API REST
 *
 * Centraliza todas las llamadas HTTP. Agrega automáticamente
 * el token Bearer en cada petición autenticada.
 *
 * Flujo arquitectural:
 *   frontend JS → api.js (fetch + Bearer) → Django API REST
 *
 * Todos los métodos devuelven { ok: bool, status: int, data: any }.
 */

const BASE_URL = '';   // Misma origin (Django sirve el frontend)

const Api = {
    // ── Utilidades internas ─────────────────────────────────────────────

    /** Construye los headers base con el token JWT del Storage */
    _headers(extra = {}) {
        const token = Storage.getToken();
        const base = { 'Content-Type': 'application/json' };
        if (token) base['Authorization'] = `Bearer ${token}`;
        return { ...base, ...extra };
    },

    /**
     * Wrapper genérico de fetch. Devuelve siempre un objeto estándar:
     * { ok, status, data }
     */
    async _request(method, path, body = null) {
        const url = `${BASE_URL}${path}`;
        const options = {
            method,
            headers: this._headers(),
        };
        if (body !== null) {
            options.body = JSON.stringify(body);
        }

        // Emitir evento para que el logger de UI lo capte
        window.dispatchEvent(new CustomEvent('api:request', {
            detail: { method, url, body }
        }));

        try {
            const response = await fetch(url, options);
            let data = null;
            try {
                data = await response.json();
            } catch {
                data = null;
            }

            window.dispatchEvent(new CustomEvent('api:response', {
                detail: { method, url, status: response.status, data }
            }));

            return { ok: response.ok, status: response.status, data };
        } catch (err) {
            window.dispatchEvent(new CustomEvent('api:response', {
                detail: { method, url, status: 0, data: null, error: err.message }
            }));
            return { ok: false, status: 0, data: null, error: err.message };
        }
    },

    // ── Auth ────────────────────────────────────────────────────────────

    /** POST /api/auth/login — Autenticación con correo y password */
    login(correo, password) {
        return this._request('POST', '/api/auth/login', { correo, password });
    },

    /** GET /api/auth/perfil — Verificar token y obtener datos del usuario */
    getPerfil() {
        return this._request('GET', '/api/auth/perfil');
    },

    // ── Compañías ───────────────────────────────────────────────────────

    /** GET /api/companias — Listar todas las compañías */
    getCompanias(pagina = 1, tamano = 25, buscar = '') {
        const qs = `?pagina=${pagina}&tamano=${tamano}&buscar=${encodeURIComponent(buscar)}`;
        return this._request('GET', `/api/companias${qs}`);
    },

    /** GET /api/companias/{id} — Obtener una compañía por ID */
    getCompaniaById(id) {
        return this._request('GET', `/api/companias/${id}`);
    },

    /** POST /api/companias — Crear una compañía */
    createCompania(data) {
        return this._request('POST', '/api/companias', data);
    },

    /** POST /api/companias/con-empleados — Crear compañía con empleados (transaccional) */
    createCompaniaConEmpleados(data) {
        return this._request('POST', '/api/companias/con-empleados', data);
    },

    /** PUT /api/companias/{id} — Actualizar completamente una compañía (Bogotá) */
    updateCompania(id, data) {
        return this._request('PUT', `/api/companias/${id}`, data);
    },

    /** PATCH /api/companias/{id} — Actualizar parcialmente una compañía (Bogotá) */
    patchCompania(id, data) {
        return this._request('PATCH', `/api/companias/${id}`, data);
    },

    /** DELETE /api/companias/{id} — Eliminar una compañía (Medellín) */
    deleteCompania(id) {
        return this._request('DELETE', `/api/companias/${id}`);
    },

    // ── Empleados ───────────────────────────────────────────────────────

    /** GET /api/empleados — Listar todos los empleados */
    getEmpleados(pagina = 1, tamano = 25, buscar = '') {
        const qs = `?pagina=${pagina}&tamano=${tamano}&buscar=${encodeURIComponent(buscar)}`;
        return this._request('GET', `/api/empleados${qs}`);
    },

    /** GET /api/empleados/{id} — Obtener un empleado por ID */
    getEmpleadoById(id) {
        return this._request('GET', `/api/empleados/${id}`);
    },

    /** POST /api/empleados — Crear un empleado */
    createEmpleado(data) {
        return this._request('POST', '/api/empleados', data);
    },

    /**
     * POST /api/empleados/bulk — Crear empleados de forma masiva
     * @param {Array} empleados — lista de objetos empleado
     */
    bulkCreateEmpleados(empleados) {
        return this._request('POST', '/api/empleados/bulk', { empleados });
    },

    /** PUT /api/empleados/{id} — Actualizar completamente un empleado (Bogotá) */
    updateEmpleado(id, data) {
        return this._request('PUT', `/api/empleados/${id}`, data);
    },

    /** PATCH /api/empleados/{id} — Actualizar parcialmente un empleado (Bogotá) */
    patchEmpleado(id, data) {
        return this._request('PATCH', `/api/empleados/${id}`, data);
    },

    /** DELETE /api/empleados/{id} — Eliminar un empleado (Medellín) */
    deleteEmpleado(id) {
        return this._request('DELETE', `/api/empleados/${id}`);
    },
};
