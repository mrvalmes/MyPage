// Función para colorear celdas según porcentaje
function getStatusClass(percent) {
    if (percent < 75) return "status incomplete"; // rojo
    if (percent < 100) return "status pending";   // amarillo
    return "status completed";                    // verde
}

// Función para renderizar cualquier tabla de top ventas
function renderTopVentas(tableSelector, data) {
    const tbody = document.querySelector(`${tableSelector} table tbody`);
    if (!tbody) {
        console.warn(`No se encontró el tbody para ${tableSelector}`);
        return;
    }

    tbody.innerHTML = ''; // limpiar

    data.forEach((item, index) => {
        const raw = item[0] || "";  // Ej: "1016312 - CARINA DE LA CRUZ"
        const vendedor = raw.length > 10 ? raw.substring(10) : raw;
        const totalPav = item[1] ?? 0;
        const pos = index + 1;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <img src="static/images/logo.png" alt="vendedor">
                <p>${vendedor}</p>
            </td>
            <td>${totalPav}</td>
            <td><span class="${getStatusClass(100)}">${pos}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const pagosUrl = "/api/pagos?empleado_id=None";
    const pavUrl = "/api/pav";
    const topVentasUrl = "/api/top_ventas";
    const topVentasCCUrl = "/api/top_ventas_cc";

    // Cargar datos principales en paralelo
    Promise.all([
        fetch(pagosUrl).then(r => r.json()),
        fetch(pavUrl).then(r => r.json())
    ])
    .then(([dataPagos, dataPav]) => {
        const totalpagos = dataPagos.pagos || 0;
        const totalpav = dataPav.pav || 0;

        document.getElementById("clientes-value").textContent = totalpagos;
        document.getElementById("pav-value").textContent = totalpav;

        const cr = totalpagos ? ((totalpav / totalpagos) * 100).toFixed(1) : 0;
        document.getElementById("conversion-value").textContent = cr + '%';
    })
    .catch(err => console.error("Error fetch métricas:", err));

    // Cargar top ventas normal
    fetch(topVentasUrl)
        .then(r => r.ok ? r.json() : Promise.reject('Error en top_ventas'))
        .then(data => renderTopVentas('#top-empleados', data))
        .catch(err => console.error(err));

    // Cargar top ventas CC
    fetch(topVentasCCUrl)
        .then(r => r.ok ? r.json() : Promise.reject('Error en top_ventas_cc'))
        .then(data => renderTopVentas('#top-empleados-cc', data))
        .catch(err => console.error(err));
});
