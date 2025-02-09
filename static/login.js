document.getElementById('loginForm').addEventListener('submit', function (event) {
    event.preventDefault(); 

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    
    fetch('json/usuarios.json')
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
                window.location.href = 'home.html';
            } else {
                alert('Usuario o contraseña incorrectos');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar los datos de usuarios');
        });
});