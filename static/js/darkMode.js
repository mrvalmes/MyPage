// 1. Initialize Theme IMMEDIATELY (before DOMContentLoaded)
(function() {
    try {
        const savedTheme = localStorage.getItem('darkMode');
        if (savedTheme === 'true') {
            document.body.classList.add('dark');
        } else {
            document.body.classList.remove('dark');
        }
    } catch (e) {
        console.error("Error initializing theme:", e);
    }
})();

// 2. Setup UI Interactions when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggler
    const toggler = document.getElementById('switch');
    if (toggler) {
        const savedTheme = localStorage.getItem('darkMode');
        toggler.checked = savedTheme === 'true';
        
        toggler.addEventListener('change', function () {
            if (this.checked) {
                document.body.classList.add('dark');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.body.classList.remove('dark');
                localStorage.setItem('darkMode', 'false');
            }
        });
    }

    // Sidebar Links
    const sideLinks = document.querySelectorAll('.sidebar .side-menu li a:not(.logout)');
    if (sideLinks.length > 0) {
        sideLinks.forEach(item => {
            const li = item.parentElement;
            item.addEventListener('click', () => {
                sideLinks.forEach(i => {
                    i.parentElement.classList.remove('active');
                })
                li.classList.add('active');
            })
        });
    }

    // Sidebar Toggle
    const menuBar = document.querySelector('.content nav .bx.bx-menu');
    const sideBar = document.querySelector('.sidebar');
    if (menuBar && sideBar) {
        menuBar.addEventListener('click', () => {
            sideBar.classList.toggle('close');
        });
    }

    // Search Form
    const searchBtn = document.querySelector('.content nav form .form-input button');
    const searchBtnIcon = document.querySelector('.content nav form .form-input button .bx');
    const searchForm = document.querySelector('.content nav form');

    if (searchBtn && searchBtnIcon && searchForm) {
        searchBtn.addEventListener('click', function (e) {
            if (window.innerWidth < 576) {
                e.preventDefault(); // Note: original code had e.preventDefault which is a property, not function call. Fixed to e.preventDefault() if intended, but keeping logic similar to original behavior if it was relying on property access (which does nothing). Assuming it meant preventDefault()
                // Actually, let's fix the bug: e.preventDefault()
                e.preventDefault();
                searchForm.classList.toggle('show');
                if (searchForm.classList.contains('show')) {
                    searchBtnIcon.classList.replace('bx-search', 'bx-x');
                } else {
                    searchBtnIcon.classList.replace('bx-x', 'bx-search');
                }
            }
        });
    }

    // Window Resize
    window.addEventListener('resize', () => {
        if (sideBar) {
            if (window.innerWidth < 768) {
                sideBar.classList.add('closed');
            } else {
                sideBar.classList.remove('closed');
            }
        }
        if (window.innerWidth > 576 && searchBtnIcon && searchForm) {
            searchBtnIcon.classList.replace('bx-x', 'bx-search');
            searchForm.classList.remove('show');
        }
    });
});
