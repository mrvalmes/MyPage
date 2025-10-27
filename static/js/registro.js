document.getElementById('registerForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const usuario = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const nivel = document.getElementById('nivel').value;

    // Validar contraseñas iguales
    if (password !== confirmPassword) {
        alert("❌ Las contraseñas no coinciden");
        return;
    }

    // Validar seguridad de la contraseña
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$/;
    if (!passwordRegex.test(password)) {
        alert("❌ La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un carácter especial.");
        return;
    }

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ usuario, password, nivel })
        });

        const data = await response.json();

        if (response.ok) {
            alert("✅ Usuario registrado correctamente");
            window.location.href = "/home.html"; // Redirige al login
        } else {
            alert("❌ " + (data.msg || "Error en el registro"));
        }
    } catch (err) {
        console.error("Error en el registro:", err);
        alert("⚠️ Error al conectar con el servidor");
    }
});
