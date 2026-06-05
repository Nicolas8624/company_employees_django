/**
 * auth.js — Módulo de autenticación
 *
 * Maneja el flujo de login/logout y la protección de rutas.
 *
 * - Si estamos en login.html y ya hay sesión → redirige a index.html
 * - Si estamos en index.html sin sesión → redirige a login.html
 * - Ejecuta el formulario de login y guarda el token en Storage
 */

const Auth = {
    /**
     * Protección de ruta para el DASHBOARD (index.html).
     * Si no hay token, redirige al login inmediatamente.
     */
    requireAuth() {
        if (!Storage.hasSession()) {
            window.location.replace('/login');
        }
    },

    /**
     * Protección de ruta para el LOGIN (login.html).
     * Si ya hay token válido, redirige al dashboard.
     */
    redirectIfAuthenticated() {
        if (Storage.hasSession()) {
            window.location.replace('/');
        }
    },

    /**
     * Envía las credenciales al endpoint de login.
     * En caso de éxito guarda la sesión y redirige al dashboard.
     *
     * @param {string} correo
     * @param {string} password
     * @returns {Promise<{ok: boolean, errorMsg: string|null}>}
     */
    async login(correo, password) {
        const result = await Api.login(correo, password);

        if (result.ok && result.data?.token) {
            Storage.saveSession(result.data.token, result.data.usuario);
            return { ok: true, errorMsg: null };
        }

        // Extraer mensaje de error de la respuesta
        const errorMsg =
            result.data?.mensaje ||
            result.data?.detail ||
            result.data?.non_field_errors?.[0] ||
            'Credenciales inválidas. Verifica tu correo y contraseña.';

        return { ok: false, errorMsg };
    },

    /**
     * Cierra la sesión: limpia el storage y redirige al login.
     */
    logout() {
        Storage.clearSession();
        window.location.replace('/login');
    },

    /**
     * Verifica el token actual llamando al endpoint /api/auth/perfil.
     * Si el token expiró o es inválido cierra la sesión.
     *
     * @returns {Promise<object|null>} datos del usuario o null
     */
    async verifySession() {
        const result = await Api.getPerfil();
        if (result.ok && result.data) {
            // Actualizar datos del usuario en Storage (por si cambiaron)
            Storage.saveSession(Storage.getToken(), result.data);
            return result.data;
        }
        // Token inválido o expirado
        this.logout();
        return null;
    },
};
