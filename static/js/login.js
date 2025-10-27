/*document.getElementById('loginForm').addEventListener('submit', function (event) {
    event.preventDefault(); 

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    
    fetch('/static/data/usuarios.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cargar los datos de usuarios');
            }
            return response.json();
        })
        .then(users => {
            
            const user = users.find(user => user.email === email && user.password === password);
            if (user) {
                //alert('Inicio de sesión exitoso');
                window.location.href = '/home';
            } else {
                alert('Usuario o contraseña incorrectos');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar los datos de usuarios');
        });
});*/

document.getElementById('loginForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            window.location.href = '/home';
        } else {
            alert(data.msg);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error en el servidor');
    }
});

// Cerrar sesión manual
function logout() {
    const token = localStorage.getItem('token');
    fetch('/logout', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token }
    }).then(() => {
        localStorage.removeItem('token');
        window.location.href = '/';
    });
}

// Auto logout tras 5 minutos de inactividad
let inactivityTimer;
function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
        logout();
        alert("Sesión expirada por inactividad");
    }, 5 * 60 * 1000);
}

document.addEventListener("mousemove", resetInactivityTimer);
document.addEventListener("keydown", resetInactivityTimer);
resetInactivityTimer();
