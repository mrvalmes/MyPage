// comisiones_role.js
// Manejo específico de rol para página de comisiones

document.addEventListener('DOMContentLoaded', async function() {
    await initComisionesRole();
});

async function initComisionesRole() {
    try {
        // Obtener info del usuario
        const token = localStorage.getItem('token');
        const response = await fetch('/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) return;
        
        const userInfo = await response.json();
        
        // Si es VENTAS, filtrar dropdown
        if (userInfo.nivel === 'ventas') {
            const empleadoSelect = document.getElementById('employeeSelect');
            
            if (empleadoSelect) {
                // Limpiar opciones
                empleadoSelect.innerHTML = '';
                
                // Agregar solo su opción
                const option = document.createElement('option');
                option.value = userInfo.codigo_usuario;
                option.textContent = userInfo.nombre_empleado || userInfo.codigo_usuario;
                option.selected = true;
                empleadoSelect.appendChild(option);
                
                // Deshabilitar el select
                empleadoSelect.disabled = true;
                empleadoSelect.style.opacity = '0.5';
                empleadoSelect.style.cursor = 'not-allowed';
            }
        }
    } catch (error) {
        console.error('Error al inicializar comisiones por rol:', error);
    }
}
