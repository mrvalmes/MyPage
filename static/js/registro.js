// registro.js
document.addEventListener('DOMContentLoaded', function() {
    // Cargar lista de empleados al iniciar
    cargarEmpleados();
    
    // Manejar el envío del formulario
    document.getElementById('registerForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const codigo_usuario = document.getElementById('codigo_usuario').value;
        const nivel = document.getElementById('nivel').value;
        
        // Validaciones
        if (password !== confirmPassword) {
            alert('Las contraseñas no coinciden');
            return;
        }
        
        if (password.length < 6) {
            alert('La contraseña debe tener al menos 6 caracteres');
            return;
        }
        
        if (!codigo_usuario) {
            alert('Debe seleccionar un empleado');
            return;
        }
        
        if (!nivel) {
            alert('Debe seleccionar un rol');
            return;
        }
        
        // Enviar petición de registro
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    usuario: email,
                    password: password,
                    codigo_usuario: codigo_usuario,
                    nivel: nivel
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('Usuario registrado correctamente. ID: ' + data.id);
                // Limpiar formulario
                document.getElementById('registerForm').reset();
                // Opcional: redirigir al login
                window.location.href = '/';
            } else {
                alert('Error: ' + data.msg);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
        }
    });
});

async function cargarEmpleados() {
    try {
        const response = await fetch('/api/empleados');
        
        if (!response.ok) {
            throw new Error('Error al cargar empleados');
        }
        
        const empleados = await response.json();
        const select = document.getElementById('codigo_usuario');
        
        // Limpiar opciones existentes (excepto la primera)
        select.innerHTML = '<option value="">-Seleccione un empleado-</option>';
        
        // Agregar opciones
        empleados.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = `${emp.id} - ${emp.nombre} (${emp.puesto})`;
            select.appendChild(option);
        });
        
        console.log(`✅ ${empleados.length} empleados cargados`);
    } catch (error) {
        console.error('Error al cargar empleados:', error);
        alert('No se pudo cargar la lista de empleados');
    }
}
