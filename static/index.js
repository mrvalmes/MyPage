const sideMenu = document.querySelector('aside');
const menuBtn = document.getElementById('menu-btn');
const closeBtn = document.getElementById('close-btn');

menuBtn.addEventListener('click', () => {
    sideMenu.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    sideMenu.style.display = 'none';
});

//contro desplegable, dropdown
document.addEventListener("DOMContentLoaded", function() {
    const dropdown = document.getElementById("opciones");

    dropdown.addEventListener("change", function() {
        const selectedOption = dropdown.options[dropdown.selectedIndex].value;
        console.log("Opción seleccionada:", selectedOption);
        //agregar lógica según la opción seleccionada
    });
});


