document.addEventListener('DOMContentLoaded', () => {
  const objetivosResultadosTableBody = document.querySelector('#obj-rest table tbody');
  //const incentivos = document.querySelector('#incentivo table tbody'); //tabla de incentivos
  if (!objetivosResultadosTableBody) {
    console.error("No se encontró el <tbody> de la tabla objetivos/resultados.");
    return;
  }

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
  // Mapeo de las columnas en "objetivos" vs "resultados"
  // claveObj es la key en data.objetivos,
  // claveRes es la key en data.resultados
  // label => texto a mostrar en la columna "Producto"
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
    // En caso de (recargas, fijos_hfc_dth, etc.)
  ];
  // Mapeo de las columnas en "resultados" para obtener la suma de PAV
  const mapPav = [
    //{ label: "Sim Card Prepago", claveObj: "sim_card_prepago", claveRes: "Card" },
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

  
  // Traer de la URL o de un <select>:
  // Obtener empleados 
  //const empleadoId = employeeSelect.value;
  const selects = document.querySelectorAll('#employeeSelect, #supervisoreSelect');
  selects.forEach(sel => {    
    sel.addEventListener('change', (event) => {
      const selectId = event.target.id;
      const empleadoId = event.target.value;      
      
      let url = '';

      if (selectId !== 'None') {
        url = `/api/objetivos-y-resultados?empleado_id=${empleadoId}`;  
          
      } else {
        url = `/api/objetivos-y-resultados?empleado_id=${empleadoId}`;
        
      
      }   
    
    // Hacer la petición al endpoint con el empleado id
      fetch(url).then(response => {
      if (!response.ok) {
        throw new Error('Error al cargar los objetivos/resultados');
      }
      return response.json();
      })
    .then(data => {
      // data => { "objetivos": {...}, "resultados": {...} }
      const objetivos = data.objetivos || {};
      const resultados = data.resultados || {};
      const totalpagos = data.pagos || 0;
      document.getElementById("clientes-value").textContent = totalpagos;

      // Llenar filas
      objetivosResultadosTableBody.innerHTML = ''; // limpiar
      // Llenar filas
      //incentivos.innerHTML = ''; // limpiar

      mapProductos.forEach(item => {
        // Obtener objetivo y resultado
        // Ojo: pueden ser string en "objetivos", conviene parsear a number
        const objNum = parseFloat(objetivos[item.claveObj]) || 0;
        const resNum = parseFloat(resultados[item.claveRes]) || 0;

        // Calcular Logro (%)
        let logro = 0;
        if (objNum > 0) {
          logro = (resNum / objNum) * 100;
        }
        logro = logro.toFixed(2);

        // Calcular Proyección, ejemplo:
        // "Si quedan X días del mes, proyectar un total al final del mes"
        let proyeccion = 0;
        //let comision = 0;
        // EJEMPLO (proyección lineal):
        const hoy = new Date();
        const dia = hoy.getDate();        // 1..31
        const diasEnMes = new Date(hoy.getFullYear(), hoy.getMonth() - 3, 0).getDate();
        // proyección
        if (dia > 0 && diasEnMes > 0) {
          proyeccion = (logro / dia) * diasEnMes;
        }
        proyeccion = proyeccion.toFixed(2);

        // Determinar clases CSS
        const logroClass = getStatusClass(logro);
        const proyeccionClass = getStatusClass(proyeccion);

        // Crear <tr>
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${item.label}</td>
          <td>${objNum}</td>
          <td>${resNum}</td>
          <td><span class="${logroClass}">${logro}%</span></td>    
          <td><span class="${proyeccionClass}">${proyeccion}%</span></td>           
        `;
        
        //obtener la suma de los resultados, excluyendo los card.
        let sumaPav = 0;
        mapPav.forEach(item => {
          const pav = parseFloat(resultados[item.claveRes]) || 0;
          sumaPav += pav;
        });     

        // Actualizar los valores en el HTML *UNA SOLA VEZ*, después de calcular la suma
        document.getElementById("pav-value").textContent = sumaPav;
        
        let cr = 0;

        if (totalpagos !== 0) {
          cr = (sumaPav / totalpagos) * 100;          
          cr = cr.toFixed(1);  
        }
        
        // Actua;izar el Coversion rate.
        document.getElementById("conversion-value").textContent = cr + '%'; // O el valor que corresponda
        
        //document.getElementById("comision-value").textContent = comision; // O el valor que corresponda

        objetivosResultadosTableBody.appendChild(tr);
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
  });
  });
});
