/**
 * permissions.js — Módulo de control de permisos por ciudad
 *
 * Implementa las REGLAS DE NEGOCIO de la Actividad 7:
 *
 * MEDELLÍN → puede: GET, POST, POST masivo, DELETE
 *            NO puede: PUT, PATCH
 *
 * BOGOTÁ   → puede: GET, POST, POST masivo, PUT, PATCH
 *            NO puede: DELETE
 *
 * Estas restricciones se aplican TANTO en la UI (ocultar/deshabilitar)
 * COMO mostrando mensajes claros si el usuario intenta la acción.
 */

const Permissions = {
    /**
     * Normaliza un string de ciudad eliminando tildes y pasando a minúsculas.
     * Permite comparar "Medellín", "medellin", "MEDELLIN", etc.
     */
    _normalizeCity(ciudad) {
        return (ciudad || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    },

    /** Detecta si el usuario es de Medellín */
    isMedellin(user) {
        if (!user) return false;
        return this._normalizeCity(user.ciudad) === 'medellin';
    },

    /** Detecta si el usuario es de Bogotá */
    isBogota(user) {
        if (!user) return false;
        return this._normalizeCity(user.ciudad) === 'bogota';
    },

    // ── Permisos individuales por operación ──────────────────────────────

    /** GET ALL y GET BY ID — permitido para todos */
    canGet(user) { return !!user; },

    /** POST (crear) — permitido para todos */
    canPost(user) { return !!user; },

    /** POST masivo (bulk) — permitido para todos */
    canBulk(user) { return !!user; },

    /**
     * PUT (actualizar completo)
     * Medellín: NO puede | Bogotá: SÍ puede
     */
    canPut(user) {
        if (!user) return false;
        return this.isBogota(user);
    },

    /**
     * PATCH (actualizar parcial)
     * Medellín: NO puede | Bogotá: SÍ puede
     */
    canPatch(user) {
        if (!user) return false;
        return this.isBogota(user);
    },

    /**
     * DELETE (eliminar)
     * Medellín: SÍ puede | Bogotá: NO puede
     */
    canDelete(user) {
        if (!user) return false;
        return this.isMedellin(user);
    },

    /**
     * Devuelve un texto descriptivo de las políticas activas para el usuario.
     */
    getPolicyDescription(user) {
        if (!user) return '';

        if (this.isMedellin(user)) {
            return `
                <strong>Usuario de Medellín:</strong> Tienes acceso a:
                <span class="perm-allowed">GET</span>
                <span class="perm-allowed">POST</span>
                <span class="perm-allowed">BULK</span>
                <span class="perm-allowed">DELETE</span>
                — Operaciones bloqueadas:
                <span class="perm-denied">PUT</span>
                <span class="perm-denied">PATCH</span>
            `;
        }
        if (this.isBogota(user)) {
            return `
                <strong>Usuario de Bogotá:</strong> Tienes acceso a:
                <span class="perm-allowed">GET</span>
                <span class="perm-allowed">POST</span>
                <span class="perm-allowed">BULK</span>
                <span class="perm-allowed">PUT</span>
                <span class="perm-allowed">PATCH</span>
                — Operación bloqueada:
                <span class="perm-denied">DELETE</span>
            `;
        }
        // Usuario sin ciudad definida — acceso básico
        return '<strong>Sesión activa.</strong> Sin restricciones de ciudad específicas.';
    },

    /**
     * Mensaje de error cuando se intenta una acción no permitida.
     */
    getDeniedMessage(action, user) {
        const city = user?.ciudad || 'tu ciudad';
        const messages = {
            PUT:    `Los usuarios de ${city} no pueden editar registros con PUT.`,
            PATCH:  `Los usuarios de ${city} no pueden editar registros con PATCH.`,
            DELETE: `Los usuarios de ${city} no pueden eliminar registros (DELETE).`,
        };
        return messages[action] || `Acción ${action} no permitida para tu perfil.`;
    },
};
