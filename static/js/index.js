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

    // Asegurar que data es un array
    if (!Array.isArray(data)) {
        console.error("Data no es un array:", data);
        return;
    }

    // Ordenar por total_pav descendente (por si acaso) y tomar top 10
    const top10 = data
        .sort((a, b) => (b.total_pav || 0) - (a.total_pav || 0))
        .slice(0, 10);

    top10.forEach((item, index) => {
        // Manejar tanto formato array [nombre, val] como objeto {nombre, total_pav}
        let rawName = "";
        let total = 0;

        if (Array.isArray(item)) {
            rawName = item[0] || "";
            total = item[1] ?? 0;
        } else {
            rawName = item.nombre || "";
            total = item.total_pav ?? 0;
        }

        // Limpiar nombre: omitir los primeros 10 caracteres si es largo
        const vendedor = rawName.length > 10 ? rawName.substring(10) : rawName;
        const pos = index + 1;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <img src="static/images/logo.png" alt="vendedor">
                <p>${vendedor}</p>
            </td>
            <td>${total}</td>
            <td><span class="${getStatusClass(100)}">${pos}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const pagosUrl = "/api/pagos?empleado_id=None";
    const pavUrl = "/api/pav";
    const recargas = "/api/recargas";    
    const topVentasCCUrl = "/api/top_ventas_cc";

    // Cargar datos principales en paralelo
    Promise.all([
        fetch(pagosUrl).then(r => r.json()),
        fetch(pavUrl).then(r => r.json()),
        fetch(recargas).then(r => r.json())
    ])
    .then(([dataPagos, dataPav, dataRecargas]) => {
        const totalpagos = dataPagos.pagos || 0;
        const totalpav = dataPav.pav || 0;
        const totalrecargas = dataRecargas.recargas || 0;

        document.getElementById("recargas-value").textContent = '$' + totalrecargas.toLocaleString('en-US');
        document.getElementById("clientes-value").textContent = totalpagos.toLocaleString('en-US');
        document.getElementById("pav-value").textContent = totalpav.toLocaleString('en-US');

        const cr = totalpagos ? ((totalpav / totalpagos) * 100).toFixed(1) : 0;
        document.getElementById("conversion-value").textContent = cr + '%';
    })
    .catch(err => console.error("Error fetch métricas:", err));
    
    
    // Cargar top ventas CC
    fetch(topVentasCCUrl)
        .then(r => r.ok ? r.json() : Promise.reject('Error en top_ventas_cc'))
        .then(data => renderTopVentas('#top-empleados-cc', data))
        .catch(err => console.error('Error cargando Top CC:', err));
});
