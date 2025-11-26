// Obtener los elementos del DOM
var modalEmpleados = document.getElementById("modal-empleados");
var modalTiendas = document.getElementById("modal-tiendas");

var btnEmpleados = document.getElementById("btn-empleados");
var btnTiendas = document.getElementById("btn-tiendas");

var spanEmpleados = modalEmpleados.getElementsByClassName("close")[0];
var spanTiendas = modalTiendas.getElementsByClassName("close")[0];

// Cuando el usuario hace clic en el botón, abre el modal correspondiente
btnEmpleados.onclick = function () {
    modalEmpleados.style.display = 'flex';
    // retraso para que la transición funcione correctamente
    setTimeout(() => {
        modalEmpleados.classList.add('show');
    }, 10);
}

btnTiendas.onclick = function () {
    modalTiendas.style.display = 'flex';
}

// Cuando el usuario hace clic en la 'x', cierra el modal
spanEmpleados.onclick = function () {
    modalEmpleados.classList.remove('show');
    // Esperar a que termine la animación antes de ocultar completamente
    setTimeout(() => {
        modalEmpleados.style.display = 'none';
    }, 250); // Mismo tiempo que la duración de la transición (0.3s)
}

spanTiendas.onclick = function () {
    modalTiendas.style.display = "none";
}

// Logic for Create User Form
const createUserForm = document.getElementById('createUserForm');
if (createUserForm) {
    createUserForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const usuario = document.getElementById('new_usuario').value;
        const codigo_usuario = document.getElementById('new_codigo_usuario').value;
        const nivel = document.getElementById('new_nivel').value;
        const temp_password = document.getElementById('temp_password').value;

        // Show loader
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.display = 'flex';
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/admin/create-user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                },
                body: JSON.stringify({
                    usuario,
                    codigo_usuario,
                    nivel,
                    temp_password
                })
            });

            const data = await response.json();

            // Hide loader
            if (loader) {
                loader.style.display = 'none';
            }

            if (response.ok) {
                alert(data.msg);
                createUserForm.reset();
                // Close modal
                modalEmpleados.classList.remove('show');
                setTimeout(() => {
                    modalEmpleados.style.display = 'none';
                }, 250);
            } else {
                alert(data.msg || "Error al crear usuario");
            }
        } catch (error) {
            // Hide loader
            if (loader) {
                loader.style.display = 'none';
            }
            console.error("Error:", error);
            alert("Error de conexión");
        }
    });
}