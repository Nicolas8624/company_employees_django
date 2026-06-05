/**
 * storage.js — Módulo de almacenamiento en LocalStorage
 *
 * Centraliza toda la persistencia del lado cliente para token
 * y datos del usuario autenticado.
 *
 * Flujo: login → guardar token + usuario → leer en cada petición
 */

const STORAGE_KEYS = {
    TOKEN: 'eh_token',
    USER: 'eh_user',
};

const Storage = {
    /** Guarda el token JWT y los datos del usuario tras un login exitoso */
    saveSession(token, user) {
        localStorage.setItem(STORAGE_KEYS.TOKEN, token);
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    },

    /** Devuelve el token JWT almacenado, o null si no existe */
    getToken() {
        return localStorage.getItem(STORAGE_KEYS.TOKEN) || null;
    },

    /** Devuelve el objeto usuario (parseado) o null si no existe */
    getUser() {
        const raw = localStorage.getItem(STORAGE_KEYS.USER);
        if (!raw) return null;
        try {
            return JSON.parse(raw);
        } catch {
            return null;
        }
    },

    /** Elimina toda la sesión del almacenamiento local */
    clearSession() {
        localStorage.removeItem(STORAGE_KEYS.TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
    },

    /** Indica si existe una sesión activa (token presente) */
    hasSession() {
        return !!this.getToken();
    },
};
