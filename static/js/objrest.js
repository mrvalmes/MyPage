document.addEventListener('DOMContentLoaded', () => {
  const objetivosResultadosTableBody = document.querySelector('#obj-rest table tbody');  

  if (!objetivosResultadosTableBody) {
    console.error("No se encontró el <tbody> de la tabla objetivos/resultados o Conversion-Rate.");
    return;
  }

  function getStatusClass(percent) {
    if (percent < 75) return "status incomplete";
    if (percent < 100) return "status pending";
    return "status completed";
  }

  const mapProductos = [
    { label: "Sim Card Prepago", claveObj: "sim_card_prepago", claveRes: "Card" },
    { label: "Flex/Max", claveObj: "flex_max", claveRes: "Flex/Max" },
    { label: "Internet", claveObj: "internet_pospago", claveRes: "Internet" },
    { label: "Migraciones", claveObj: "migraciones_pospago_net", claveRes: "Migraciones" },
    { label: "FidePuntos Pos", claveObj: "fidepuntos_pospago", claveRes: "Fidepuntos Pos" },
    { label: "FidePuntos Up", claveObj: "fidepuntos_up", claveRes: "Fidepuntos Up" },
    { label: "Reemplazo Pos", claveObj: "reemplazo_pospago", claveRes: "Reemplazo Pos" },
    { label: "Reemplazo Up", claveObj: "reemplazo_up", claveRes: "Reemplazo Up" },
    { label: "Fide Reemp Net Up", claveObj: "fide_reemp_internet_up", claveRes: "Fide Reemp Internet Up" },
    { label: "Aumentos Plan Pos/Net", claveObj: "aumentos_plan_pos_net", claveRes: "Aumentos" }
  ];

  const mapPav = [
    { claveRes: "Flex/Max" },
    { claveRes: "Internet" },
    { claveRes: "Migraciones" },
    { claveRes: "Fidepuntos Pos" },
    { claveRes: "Fidepuntos Up" },
    { claveRes: "Reemplazo Pos" },
    { claveRes: "Reemplazo Up" },
    { claveRes: "Fide Reemp Internet Up" },
    { claveRes: "Aumentos" }
  ];

  const pagosUrl = "/api/pagos?empleado_id=None";
  const pavUrl = "/api/pav";

      // Cargar datos principales en paralelo: PAV , CLIENTES Y CR General.
    Promise.all([
        fetch(pagosUrl).then(r => r.json()),
        fetch(pavUrl).then(r => r.json())
    ])
    .then(([dataPagos, dataPav]) => {
        const totalpagos = dataPagos.pagos || 0;
        const totalpav = dataPav.pav || 0;

        document.getElementById("clientes-value").textContent = totalpagos.toLocaleString('en-US');
        document.getElementById("pav-value").textContent = totalpav.toLocaleString('en-US');

        const cr = totalpagos ? ((totalpav / totalpagos) * 100).toFixed(1) : 0;
        document.getElementById("conversion-value").textContent = cr + '%';
    })
    .catch(err => console.error("Error fetch métricas:", err));


  const selects = document.querySelectorAll('#employeeSelect, #supervisoreSelect');

  selects.forEach(sel => {    
    sel.addEventListener('change', (event) => {
      const empleadoId = event.target.value;      

      if (!empleadoId || empleadoId === 'None') return;

      const pagosUrl = `/api/pagos?empleado_id=${empleadoId}`;
      const url = `/api/objetivos-y-resultados?empleado_id=${empleadoId}`;

      // Ejecutar ambas peticiones y esperar las respuestas
      Promise.all([
        fetch(pagosUrl).then(r => r.json()),
        fetch(url).then(r => r.json())
      ])
      .then(([pagosData, objetivosData]) => {
        const pagos = pagosData.pagos || 0;
        document.getElementById("clientes-value").textContent = pagos.toLocaleString('en-US');

        const objetivos = objetivosData.objetivos || {};
        const resultados = objetivosData.resultados || {};
        const totalpagos = parseFloat(pagos) || 0;

        // Llenar la tabla
        objetivosResultadosTableBody.innerHTML = '';
        mapProductos.forEach(item => {
          const objNum = parseFloat(objetivos[item.claveObj]) || 0;
          const resNum = parseFloat(resultados[item.claveRes]) || 0;

          let logro = (objNum > 0) ? (resNum / objNum) * 100 : 0;
          logro = logro.toFixed(2);

          const hoy = new Date();
          const dia = hoy.getDate();
          const diasEnMes = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0).getDate();
          let proyeccion = (dia > 0) ? (logro / dia) * diasEnMes : 0;
          proyeccion = proyeccion.toFixed(2);

          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${item.label}</td>
            <td>${objNum}</td>
            <td>${resNum}</td>
            <td><span class="${getStatusClass(logro)}">${logro}%</span></td>    
            <td><span class="${getStatusClass(proyeccion)}">${proyeccion}%</span></td>
          `;
          objetivosResultadosTableBody.appendChild(tr);
        });

        // Calcular PAV y CR
        let sumaPav = 0;
        mapPav.forEach(item => {
          const pav = parseFloat(resultados[item.claveRes]) || 0;
          sumaPav += pav;
        });

        document.getElementById("pav-value").textContent = sumaPav;
        let cr = (totalpagos > 0 && sumaPav > 0) ? ((sumaPav / totalpagos) * 100).toFixed(2) : 0;
        document.getElementById("conversion-value").textContent = cr + '%';
      })
      .catch(error => console.error('Error cargando datos:', error));
    });
  });
});
