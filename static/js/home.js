
// Obtener empleados
const selectEmpleado = document.getElementById('employeeSelect');
const selectSupervisor = document.getElementById('supervisoreSelect');

function cargarDatos() {
    // 1) Llamamos las dos APIs en paralelo
    Promise.all([
        fetch('/api/empleados'),
        fetch('/api/supervisor')
    ])
        .then(([respEmpleados, respSupervisores]) => {
            // 2) Convertimos ambas respuestas a JSON
            return Promise.all([
                respEmpleados.json(),
                respSupervisores.json()
            ]);
        })
        .then(([listaEmpleados, listaSupervisores]) => {
            // 3) Llenar el dropdown de empleados
            selectEmpleado.innerHTML = '';
            const optDefaultEmp = document.createElement('option');
            optDefaultEmp.value = "";
            optDefaultEmp.textContent = "Selecciona Empleado";
            selectEmpleado.appendChild(optDefaultEmp)

            listaEmpleados.forEach(emp => {
                const option = document.createElement('option');
                option.value = emp.id;       // ID único
                option.textContent = emp.nombre; // Nombre del empleado
                selectEmpleado.appendChild(option);
            });

            // 4) Llenar el dropdown de supervisores
            selectSupervisor.innerHTML = '';
            const optDefaultSup = document.createElement('option');
            optDefaultSup.value = "";
            optDefaultSup.textContent = "Selecciona Supervisor";
            selectSupervisor.appendChild(optDefaultSup);

            listaSupervisores.forEach(sup => {
                const option = document.createElement('option');
                option.value = sup.id;        // ID único
                option.textContent = sup.nombre; // Nombre del supervisor
                selectSupervisor.appendChild(option);
            });
        })
        .catch(error => console.error("Error al cargar datos:", error));
}
// Llamar la función al cargar la página
cargarDatos()