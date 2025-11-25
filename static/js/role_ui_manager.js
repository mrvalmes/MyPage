// role_ui_manager.js
// Maneja la UI según el rol del usuario

let currentUserInfo = null;

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', async function() {
    await loadUserInfo();
    adjustUIByRole();
});

async function loadUserInfo() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            currentUserInfo = await response.json();
            console.log('Usuario actual:', currentUserInfo);
        }
    } catch (error) {
        console.error('Error al cargar info de usuario:', error);
    }
}

function adjustUIByRole() {
    if (!currentUserInfo) return;
    
    const nivel = currentUserInfo.nivel;
    
    // Ocultar menús según rol
    hideMenusByRole(nivel);
    
    // Ajustar dropdowns y controles
    adjustControlsByRole(nivel);
    
    // Actualizar foto de perfil
    updateProfileImage();
}

function updateProfileImage() {
    if (!currentUserInfo) return;
    
    const profileLink = document.querySelector('nav .profile');
    const profileImg = document.querySelector('nav .profile img');
    
    if (profileLink && profileImg) {
        // 1. Actualizar Imagen
        if (currentUserInfo.codigo_usuario) {
            const imagePath = `/static/images/${currentUserInfo.codigo_usuario}.jpg`;
            profileImg.src = imagePath;
            
            profileImg.onerror = function() {
                this.src = '/static/images/logo.png';
                this.onerror = null;
            };
        }
        
        // 2. Inyectar Nombre y Rol (si no existen ya)
        let infoContainer = profileLink.querySelector('.user-info');
        
        if (!infoContainer) {
            infoContainer = document.createElement('div');
            infoContainer.className = 'user-info';
            infoContainer.style.display = 'flex';
            infoContainer.style.flexDirection = 'column';
            infoContainer.style.alignItems = 'flex-end';
            infoContainer.style.marginRight = '10px';
            infoContainer.style.lineHeight = '1.2';
            
            // Insertar antes de la imagen
            profileLink.insertBefore(infoContainer, profileImg);
            
            // Ajustar estilo del link para que se vea bien flex
            profileLink.style.display = 'flex';
            profileLink.style.alignItems = 'center';
            profileLink.style.textDecoration = 'none'; // Quitar subrayado si tiene
            profileLink.style.color = 'inherit'; // Heredar color de texto
        }
        
        // Actualizar textos
        // Nombre
        let nameSpan = infoContainer.querySelector('.user-name');
        if (!nameSpan) {
            nameSpan = document.createElement('span');
            nameSpan.className = 'user-name';
            nameSpan.style.fontWeight = '600';
            nameSpan.style.fontSize = '14px';
            nameSpan.style.color = 'var(--dark)'; // Color dinámico según tema
            infoContainer.appendChild(nameSpan);
        }
        // Usar nombre_empleado o nombre o codigo como fallback
        nameSpan.textContent = currentUserInfo.nombre_empleado || currentUserInfo.nombre || currentUserInfo.codigo_usuario || 'Usuario';
        
        // Rol
        let roleSpan = infoContainer.querySelector('.user-role');
        if (!roleSpan) {
            roleSpan = document.createElement('span');
            roleSpan.className = 'user-role';
            roleSpan.style.fontSize = '11px';
            roleSpan.style.color = 'var(--text-color, #888)'; // Usar variable CSS si existe, o gris
            roleSpan.style.opacity = '0.8';
            roleSpan.style.textTransform = 'capitalize'; // Primera letra mayúscula
            infoContainer.appendChild(roleSpan);
        }
        roleSpan.textContent = currentUserInfo.nivel || 'Usuario';
        
        console.log('Perfil actualizado con imagen y datos');
    }
}

function hideMenusByRole(nivel) {
    // Buscar los enlaces del menú por href parcial
    const allLinks = document.querySelectorAll('.side-menu a');
    const menuItems = {
        'home': null,
        'procesos': null,
        'mantenimientos': null
    };
    
    // Encontrar los enlaces correctos
    allLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href.includes('home')) menuItems.home = link;
        if (href && href.includes('procesos')) menuItems.procesos = link;
        if (href && href.includes('Mantenimientos')) menuItems.mantenimientos = link;
    });
    
    if (nivel === 'ventas') {
        // Ocultar Home, Procesos y Mantenimientos para VENTAS
        if (menuItems.home) menuItems.home.parentElement.style.display = 'none';
        if (menuItems.procesos) menuItems.procesos.parentElement.style.display = 'none';
        if (menuItems.mantenimientos) menuItems.mantenimientos.parentElement.style.display = 'none';
        console.log('Menús ocultados para usuario VENTAS');
    } else if (nivel === 'supervisor') {
        // Ocultar Procesos y Mantenimientos para SUPERVISOR
        if (menuItems.procesos) menuItems.procesos.parentElement.style.display = 'none';
        if (menuItems.mantenimientos) menuItems.mantenimientos.parentElement.style.display = 'none';
        console.log('Menús ocultados para usuario SUPERVISOR');
    }
    // ADMIN ve todo, no ocultar nada
}

function adjustControlsByRole(nivel) {
    if (nivel === 'ventas') {
        // Deshabilitar dropdown de supervisor si existe
        const supervisorSelect = document.getElementById('supervisor');
        if (supervisorSelect) {
            supervisorSelect.disabled = true;
            supervisorSelect.style.opacity = '0.5';
            supervisorSelect.style.cursor = 'not-allowed';
        }
        
        // Configurar dropdown de empleado con solo su nombre
        const empleadoSelect = document.getElementById('empleado');
        if (empleadoSelect && currentUserInfo.codigo_usuario) {
            // Limpiar opciones
            empleadoSelect.innerHTML = '';
            
            // Agregar solo su opción
            const option = document.createElement('option');
            option.value = currentUserInfo.codigo_usuario;
            option.textContent = currentUserInfo.nombre_empleado || currentUserInfo.codigo_usuario;
            option.selected = true;
            empleadoSelect.appendChild(option);
            
            // Deshabilitar el select
            empleadoSelect.disabled = true;
            empleadoSelect.style.opacity = '0.5';
            empleadoSelect.style.cursor = 'not-allowed';
            
            // Cargar datos automáticamente
            if (typeof loadDashboardData === 'function') {
                loadDashboardData(currentUserInfo.codigo_usuario);
            }
        }
        
        // Deshabilitar búsqueda de conversion rate
        const searchBtn = document.querySelector('button[onclick*="conversion"]');
        if (searchBtn) {
            searchBtn.onclick = function(e) {
                e.preventDefault();
                alert('No tiene permisos para buscar datos de otros empleados');
                return false;
            };
        }
    }
}

// Función helper para obtener info del usuario actual
function getCurrentUser() {
    return currentUserInfo;
}

// Función para verificar si es VENTAS
function isVentas() {
    return currentUserInfo && currentUserInfo.nivel === 'ventas';
}

// Función para verificar si es ADMIN
function isAdmin() {
    return currentUserInfo && currentUserInfo.nivel === 'admin';
}

// Función para verificar si es SUPERVISOR
function isSupervisor() {
    return currentUserInfo && currentUserInfo.nivel === 'supervisor';
}
