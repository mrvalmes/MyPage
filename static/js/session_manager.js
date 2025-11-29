// session_manager.js
// Manejo proactivo de sesiones expiradas
// Monitorea la actividad del usuario y detecta cuando la sesión expira (10 minutos de inactividad)

(function() {
    'use strict';
    
    // Configuración del timeout (10 minutos en milisegundos)
    const INACTIVITY_TIMEOUT = 10 * 60 * 1000; // 10 minutos
    const CHECK_INTERVAL = 30 * 1000; // Verificar cada 30 segundos
    
    let lastActivityTime = Date.now();
    let checkIntervalId = null;
    
    // Actualizar tiempo de última actividad
    function updateActivity() {
        lastActivityTime = Date.now();
    }
    
    // Verificar si la sesión ha expirado
    function checkSessionTimeout() {
        const inactiveTime = Date.now() - lastActivityTime;
        
        if (inactiveTime >= INACTIVITY_TIMEOUT) {
            handleSessionExpired('Tu sesión ha expirado por inactividad (10 minutos). Serás redirigido al login.');
        }
    }
    
    // Iniciar monitoreo de actividad
    function startActivityMonitoring() {
        // Solo monitorear si hay un token (usuario autenticado)
        if (!localStorage.getItem('token')) {
            return;
        }
        
        // Eventos que indican actividad del usuario
        const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
        
        activityEvents.forEach(event => {
            document.addEventListener(event, updateActivity, true);
        });
        
        // Verificar periódicamente si la sesión ha expirado
        checkIntervalId = setInterval(checkSessionTimeout, CHECK_INTERVAL);
    }
    
    // Detener monitoreo
    function stopActivityMonitoring() {
        if (checkIntervalId) {
            clearInterval(checkIntervalId);
            checkIntervalId = null;
        }
    }
    
    // Guardar el fetch original
    const originalFetch = window.fetch;
    
    // Sobrescribir fetch para interceptar respuestas
    window.fetch = function(...args) {
        // Actualizar actividad en cada petición
        updateActivity();
        
        return originalFetch.apply(this, args)
            .then(response => {
                // Detectar sesión expirada (código 440)
                if (response.status === 440) {
                    handleSessionExpired('Tu sesión ha expirado por inactividad. Serás redirigido al login.');
                    return Promise.reject(new Error('Sesión expirada'));
                }
                
                // Detectar sesión inválida (código 401)
                if (response.status === 401) {
                    response.clone().json().then(data => {
                        if (data.msg && (data.msg.includes('Sesión') || data.msg.includes('sesión'))) {
                            handleSessionExpired('Tu sesión es inválida o ha expirado. Serás redirigido al login.');
                        }
                    }).catch(() => {
                        // Si no se puede parsear el JSON, ignorar
                    });
                }
                
                // Detectar conflicto de sesión (código 409)
                if (response.status === 409) {
                    response.clone().json().then(data => {
                        if (data.msg && data.msg.includes('reemplazada')) {
                            handleSessionExpired('Tu sesión ha sido reemplazada en otro navegador. Serás redirigido al login.');
                        }
                    }).catch(() => {});
                }
                
                return response;
            })
            .catch(error => {
                // Si el error es de sesión expirada, no hacer nada más
                if (error.message === 'Sesión expirada') {
                    throw error;
                }
                // Para otros errores, propagarlos normalmente
                throw error;
            });
    };
    
    function handleSessionExpired(message) {
        // Evitar múltiples alertas si ya se está procesando
        if (window.sessionExpiredHandled) {
            return;
        }
        window.sessionExpiredHandled = true;
        
        // Detener monitoreo
        stopActivityMonitoring();
        
        // Limpiar datos de sesión
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
        
        // Mostrar mensaje claro al usuario
        alert(message || 'Tu sesión ha expirado. Serás redirigido al login.');
        
        // Redirigir al login
        window.location.href = '/';
    }
    
    // Iniciar monitoreo cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startActivityMonitoring);
    } else {
        startActivityMonitoring();
    }
    
    // Limpiar al salir de la página
    window.addEventListener('beforeunload', stopActivityMonitoring);
    
})();
