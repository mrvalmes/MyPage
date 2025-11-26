// session_manager.js
// Interceptor global para manejar sesiones expiradas
// El backend controla el timeout de inactividad (10 minutos)
// Este script solo detecta cuando el backend retorna código 440 y maneja la redirección

(function() {
    'use strict';
    
    // Guardar el fetch original
    const originalFetch = window.fetch;
    
    // Sobrescribir fetch para interceptar respuestas
    window.fetch = function(...args) {
        return originalFetch.apply(this, args)
            .then(response => {
                // Detectar sesión expirada (código 440)
                if (response.status === 440) {
                    handleSessionExpired();
                    // Retornar una promesa rechazada para evitar procesamiento adicional
                    return Promise.reject(new Error('Sesión expirada'));
                }
                
                // Detectar sesión inválida (código 401)
                if (response.status === 401) {
                    // Clonar la respuesta para poder leerla sin consumirla
                    response.clone().json().then(data => {
                        if (data.msg && data.msg.includes('Sesión')) {
                            handleSessionExpired();
                        }
                    }).catch(() => {
                        // Si no se puede parsear el JSON, ignorar
                    });
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
    
    function handleSessionExpired() {
        // Evitar múltiples alertas si ya se está procesando
        if (window.sessionExpiredHandled) {
            return;
        }
        window.sessionExpiredHandled = true;
        
        // Limpiar token del localStorage
        localStorage.removeItem('token');
        
        // Mostrar mensaje claro al usuario
        alert('Tu sesión ha expirado por inactividad. Serás redirigido al login.');
        
        // Redirigir al login
        window.location.href = '/';
    }
    
})();
