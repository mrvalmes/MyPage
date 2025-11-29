document.getElementById('loginForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const loginBtn = event.target.querySelector('.login-btn');
    const loader = document.getElementById('loader');
    
    const email = emailInput.value;
    const password = passwordInput.value;

    // Guardar texto original del botón
    const originalBtnText = loginBtn.textContent;

    try {
        // Mostrar estado de carga
        loginBtn.textContent = 'Iniciando sesión...';
        loginBtn.disabled = true;
        emailInput.disabled = true;
        passwordInput.disabled = true;
        
        // Mostrar loader si existe
        if (loader) {
            loader.style.display = 'flex';
        }

        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            
            if (data.force_password_change) {
                window.location.href = '/change-password';
                return;
            }

            // Redirigir según el rol del usuario
            const nivel = data.nivel;
            
            if (nivel === 'ventas') {
                // Usuario VENTAS va a dashboard (no tiene acceso a home)
                window.location.href = '/dashboard';
            } else {
                // ADMIN y SUPERVISOR van a home
                window.location.href = '/home';
            }
        } else {
            // Restaurar estado en caso de error
            loginBtn.textContent = originalBtnText;
            loginBtn.disabled = false;
            emailInput.disabled = false;
            passwordInput.disabled = false;
            
            if (loader) {
                loader.style.display = 'none';
            }
            
            alert(data.msg || 'Error al iniciar sesión');
        }
    } catch (error) {
        // Restaurar estado en caso de error
        loginBtn.textContent = originalBtnText;
        loginBtn.disabled = false;
        emailInput.disabled = false;
        passwordInput.disabled = false;
        
        if (loader) {
            loader.style.display = 'none';
        }
        
        console.error('Error:', error);
        alert('Error al conectar con el servidor');
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

// El timer de inactividad se maneja en el backend (10 minutos)
// session_manager.js detecta cuando el backend expira la sesión (código HTTP 440)
