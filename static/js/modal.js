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
    //modalEmpleados.style.display = "none";
    modalEmpleados.classList.remove('show');
    // Esperar a que termine la animación antes de ocultar completamente
    setTimeout(() => {
        modalEmpleados.style.display = 'none';
    }, 250); // Mismo tiempo que la duración de la transición (0.3s)
}

spanTiendas.onclick = function () {
    modalTiendas.style.display = "none";
}

/* Cuando el usuario hace clic fuera del modal, ciérralo
window.onclick = function (event) {
    if (event.target == modalEmpleados) {
        modalEmpleados.style.display = "none";
    }
    if (event.target == modalTiendas) {
        modalTiendas.style.display = "none";
    }
}*/