// Función para colorear celdas según porcentaje
function getStatusClass(percent) {
    if (percent < 75) {
        return "status incomplete";    // rojo
    } else if (percent < 100) {
        return "status pending";   // amarillo
    } else {
        return "status completed";   // verde
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const pagosUrl = "/api/pagos?empleado_id=None";
    const pavUrl = "/api/pav";

    // Llamar a fetch en paralelo y esperar a que ambas terminen
    Promise.all([
        fetch(pagosUrl).then(response => response.json()),
        fetch(pavUrl).then(response => response.json())
    ])
        .then(([dataPagos, dataPav]) => {
            // dataPagos = { pagos: ... }
            // dataPav   = { pav: ... }

            const totalpagos = dataPagos.pagos || 0;
            const totalpav = dataPav.pav || 0;

            // Mostrar en el DOM
            document.getElementById("clientes-value").textContent = totalpagos;
            document.getElementById("pav-value").textContent = totalpav;

            // Calcular ratio
            let cr = 0;
            if (totalpagos !== 0) {
                cr = (totalpav / totalpagos) * 100;
                cr = cr.toFixed(1);
            }
            document.getElementById("conversion-value").textContent = cr + '%';
        })
        .catch(err => console.error("Error fetch:", err));
    
    // Seleccionar el <tbody> donde insertar filas
    const topEmpleadosTableBody = document.querySelector('#top-empleados table tbody');
    if (!topEmpleadosTableBody) {
        console.error("No se encontró el <tbody> de la tabla top-empleados.");
        return;
    }

    // Hacer fetch a tu endpoint que devuelve el top de vendedores
    fetch('/api/top_ventas')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cargar top_ventas');
            }
            return response.json();
        })
        .then(data => {
            // data es un array de arrays, ej: [[vendedor, total], [vendedor2, total2], ...]
            // Limpiar filas anteriores (si fuera necesario)
            topEmpleadosTableBody.innerHTML = '';

            data.forEach((item, index) => {
                //const vendedor = item[0];                  
                const raw = item[0]; // "1016312 - CARINA DE LA CRUZ"
                const vendedor = raw.substring(10); 
                const totalPav = item[1];     
                const pos = index + 1;

                // Crear la fila <tr>
                const tr = document.createElement('tr');               

                // Estructur de <td>:
                // 1) Vendedor con imagen y nombre
                // 2) totalPav
                // 3) <td> con <span class="status XXX"></span>
                tr.innerHTML = `
          <td>
            <img src="static/images/logo.png">
            <p>${vendedor}</p>
          </td>
          <td>${totalPav}</td>
          <td><span class="status completed">${pos}</span></td>
        `;
                // Insertamos la fila en el tbody
                topEmpleadosTableBody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error:", err));
});


