const toggler = document.getElementById('switch');

// Al cargar la página, revisamos si el modo oscuro está activo en localStorage
const savedDarkMode = localStorage.getItem('darkMode');

// Si existe y es 'true', aplicamos la clase .dark al body y marcamos el checkbox
if (savedDarkMode === 'true') {
    document.body.classList.add('dark');
    toggler.checked = true;
}
// Cuando el usuario cambie el checkbox:
toggler.addEventListener('change', function () {
    if (this.checked) {
        document.body.classList.add('dark');
        // Guardar 'true' en localStorage
        localStorage.setItem('darkMode', 'true');
    } else {
        document.body.classList.remove('dark');
        // Guardar 'false'
        localStorage.setItem('darkMode', 'false');
    }
});

const sideLinks = document.querySelectorAll('.sidebar .side-menu li a:not(.logout)');

sideLinks.forEach(item => {
    const li = item.parentElement;
    item.addEventListener('click', () => {
        sideLinks.forEach(i => {
            i.parentElement.classList.remove('active');
        })
        li.classList.add('active');
    })
});

const menuBar = document.querySelector('.content nav .bx.bx-menu');
const sideBar = document.querySelector('.sidebar');

const searchBtn = document.querySelector('.content nav form .form-input button');
const searchBtnIcon = document.querySelector('.content nav form .form-input button .bx');
const searchForm = document.querySelector('.content nav form');

searchBtn.addEventListener('click', function (e) {
    if (window.innerWidth < 576) {
        e.preventDefault;
        searchForm.classList.toggle('show');
        if (searchForm.classList.contains('show')) {
            searchBtnIcon.classList.replace('bx-search', 'bx-x');
        } else {
            searchBtnIcon.classList.replace('bx-x', 'bx-search');
        }
    }
});

menuBar.addEventListener('click', () => {
    sideBar.classList.toggle('close');
});

window.addEventListener('resize', () => {
    if (window.innerWidth < 768) {
        sideBar.classList.add('closed');
    } else {
        sideBar.classList.remove('closed');
    }
    if (window.innerWidth > 576) {
        searchBtnIcon.classList.replace('bx-x', 'bx-search');
        searchForm.classList.remove('show');
    }
});
