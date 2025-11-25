// dashboard.js
// Manejo de dropdowns y carga de datos según rol

const selectEmpleado = document.getElementById('employeeSelect');
const selectSupervisor = document.getElementById('supervisoreSelect');

let userInfo = null;

async function initDashboard() {
    // Cargar información del usuario
    await loadCurrentUser();
    
    // Cargar dropdowns
    await cargarDatos();
    
    // Ajustar UI según rol
    adjustDashboardByRole();
}

async function loadCurrentUser() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            userInfo = await response.json();
            console.log('Usuario dashboard:', userInfo);
        }
    } catch (error) {
        console.error('Error al cargar usuario:', error);
    }
}

async function cargarDatos() {
    try {
        const [respEmpleados, respSupervisores] = await Promise.all([
            fetch('/api/empleados'),
            fetch('/api/supervisor'),
        ]);
        
        const [listaEmpleados, listaSupervisores] = await Promise.all([
            respEmpleados.json(),
            respSupervisores.json(),
        ]);
        
        // Llenar dropdown de empleados
        selectEmpleado.innerHTML = '';
        const optDefaultEmp = document.createElement('option');
        optDefaultEmp.value = "";
        optDefaultEmp.textContent = "-- Seleccione Vendedor --";
        selectEmpleado.appendChild(optDefaultEmp);

        listaEmpleados.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = emp.nombre;
            selectEmpleado.appendChild(option);
        });

        // Llenar dropdown de supervisores
        selectSupervisor.innerHTML = '';
        const optDefaultSup = document.createElement('option');
        optDefaultSup.value = "";
        optDefaultSup.textContent = "-- Seleccione Supervisor --";
        selectSupervisor.appendChild(optDefaultSup);

        listaSupervisores.forEach(sup => {
            const option = document.createElement('option');
            option.value = sup.id;
            option.textContent = sup.nombre;
            selectSupervisor.appendChild(option);
        });
    } catch (error) {
        console.error("Error al cargar datos:", error);
    }
}

function adjustDashboardByRole() {
    if (!userInfo) return;
    
    const nivel = userInfo.nivel;
    
    if (nivel === 'ventas') {
        // Deshabilitar dropdown de supervisor
        selectSupervisor.disabled = true;
        selectSupervisor.style.opacity = '0.5';
        selectSupervisor.style.cursor = 'not-allowed';
        
        // Configurar dropdown de empleado con solo su nombre
        selectEmpleado.innerHTML = '';
        const option = document.createElement('option');
        option.value = userInfo.codigo_usuario;
        option.textContent = userInfo.nombre_empleado || userInfo.codigo_usuario;
        option.selected = true;
        selectEmpleado.appendChild(option);
        
        // Deshabilitar el select
        selectEmpleado.disabled = true;
        selectEmpleado.style.opacity = '0.5';
        selectEmpleado.style.cursor = 'not-allowed';
        
        // Cargar automáticamente sus datos
        console.log('Cargando datos para vendedor:', userInfo.codigo_usuario);
        
        // Recargar el chart con los datos del empleado
        if (typeof fetchAndRenderChart === 'function') {
            setTimeout(() => {
                fetchAndRenderChart();
            }, 100);
        }
    }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', initDashboard);