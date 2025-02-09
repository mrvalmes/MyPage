const sideMenu = document.querySelector('aside');
const menuBtn = document.getElementById('menu-btn');
const closeBtn = document.getElementById('close-btn');

menuBtn.addEventListener('click', () => {
    sideMenu.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    sideMenu.style.display = 'none';
});

Vendedores.forEach(Vendedores => {
    const tr = document.createElement('tr');
    let statusClass = '';       

    const trContent = `
        <td>${Vendedores.nombreVend}</td>
        <td>${Vendedores.tienda}</td>
        <td>${Vendedores.supervisor}</td>
        <td class="${Vendedores.status === 'Inactivo' ? 'danger' : Vendedores.status === 'Licencia' ? 'warning' : Vendedores.status === 'Vacaciones' ? 'warning' : 'success'}">${Vendedores.status}</td>   \
    `;
    tr.innerHTML = trContent;
    document.querySelector('table tbody').appendChild(tr);
});
