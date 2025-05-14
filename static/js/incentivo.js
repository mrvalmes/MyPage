/*document.addEventListener('DOMContentLoaded', () => {
const objetivosResultadosTableBody = document.querySelector('#incentivo table tbody');
  if (!objetivosResultadosTableBody) {
    console.error("No se encontró el <tbody> de la tabla incentivo.");
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
  const mapProductos = [
    { label: "Sim Card Prepago", claveObj: "sim_card_prepago", claveRes: "Card", claveIncentivo: "sim_card_prepago" },
    { label: "Flex/Max", claveObj: "flex_max", claveRes: "Flex/Max", claveIncentivo: "flex_max" },
    { label: "Internet", claveObj: "internet_pospago", claveRes: "Internet", claveIncentivo: "internet_pospago" },
    { label: "Migraciones", claveObj: "migraciones_pospago_net", claveRes: "Migraciones", claveIncentivo: "migraciones_pospago_net" },
    { label: "FidePuntos Pos", claveObj: "fidepuntos_pospago", claveRes: "Fidepuntos Pos", claveIncentivo: "fidepuntos_pospago" },
    { label: "FidePuntos Up", claveObj: "fidepuntos_up", claveRes: "Fidepuntos Up", claveIncentivo: "fidepuntos_up" },
    { label: "Reemplazo Pos", claveObj: "reemplazo_pospago", claveRes: "Reemplazo Pos", claveIncentivo: "reemplazo_pospago" },
    { label: "Reemplazo Up", claveObj: "reemplazo_up", claveRes: "Reemplazo Up", claveIncentivo: "reemplazo_up" },
    { label: "Fide Reemp Net Up", claveObj: "fide_reemp_internet_up", claveRes: "Fide Reemp Internet Up", claveIncentivo: "fide_reemp_internet_up" },
    { label: "Aumentos Plan Pos/Net", claveObj: "aumentos_plan_pos_net", claveRes: "Aumentos", claveIncentivo: "aumentos_plan_pos_net" }
  ];

  const selects = document.querySelectorAll('#employeeSelect, #supervisoreSelect');
  selects.forEach(sel => {
    sel.addEventListener('change', (event) => {
      const selectId = event.target.id;
      const empleadoId = event.target.value;

      let url = `/api/incentivos?empleado_id=${empleadoId}`;

      fetch(url).then(response => {
        if (!response.ok) {
          throw new Error('Error al cargar los objetivos/resultados');
        }
        return response.json();
      })
        .then(data => {
          const objetivos = data.objetivos || {};
          const resultados = data.resultados || {};
          const incentivo = data.incentivo || {};          

          objetivosResultadosTableBody.innerHTML = ''; // limpiar

          let sumaPav = 0;
          mapProductos.forEach(item => {
            const objNum = parseFloat(objetivos[item.claveObj]) || 0;
            const resNum = parseFloat(resultados[item.claveRes]) || 0;
            const incentivo_75 = parseFloat(incentivo[item.claveIncentivo_75]) || 0;
            const incentivo_100 = parseFloat(incentivo[item.claveIncentivo_100]) || 0;
            console.log(objNum, resNum, incentivo_75, incentivo_100);

            let logro = 0;
            if (objNum > 0) {
              logro = (resNum / objNum) * 100;
            }
            logro = logro.toFixed(2);

            const logroClass = getStatusClass(logro);

            const tr = document.createElement('tr');
            tr.innerHTML = `
            <td>${item.label}</td>
            <td>${objNum}</td>
            <td>${resNum}</td>
            <td><span class="${logroClass}">${logro}%</span></td> 
            <td>${incentivo_75}</td>
            <td>${incentivo_100}</td>
                      
          `;

            objetivosResultadosTableBody.appendChild(tr);
            
          });
        })
        .catch(error => {
          console.error('Error:', error);
        });
    });
  });
});*/

document.addEventListener('DOMContentLoaded', () => {
  const objetivosResultadosTableBody = document.querySelector('#incentivo table tbody');
  if (!objetivosResultadosTableBody) {
    console.error("No se encontró el <tbody> de la tabla incentivo.");
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

  // Mapeo de las columnas en "objetivos" vs "resultados" vs "incentivo"
  const mapProductos = [
    { label: "Sim Card Prepago", claveObj: "sim_card_prepago", claveRes: "Card", claveIncent: "Card" },
    { label: "Flex/Max", claveObj: "flex_max", claveRes: "Flex/Max", claveIncent: "Flex/Max" },
    { label: "Internet", claveObj: "internet_pospago", claveRes: "Internet", claveIncent: "Internet" },
    { label: "Migraciones", claveObj: "migraciones_pospago_net", claveRes: "Migraciones", claveIncent: "Migraciones" },
    { label: "FidePuntos Pos", claveObj: "fidepuntos_pospago", claveRes: "Fidepuntos Pos", claveIncent: "Fidepuntos Pos" },
    { label: "FidePuntos Up", claveObj: "fidepuntos_up", claveRes: "Fidepuntos Up", claveIncent: "Fidepuntos Up" },
    { label: "Reemplazo Pos", claveObj: "reemplazo_pospago", claveRes: "Reemplazo Pos", claveIncent: "Reemplazo Pos" },
    { label: "Reemplazo Up", claveObj: "reemplazo_up", claveRes: "Reemplazo Up", claveIncent: "Reemplazo Up" },
    { label: "Fide Reemp Net Up", claveObj: "fide_reemp_internet_up", claveRes: "Fide Reemp Internet Up", claveIncent: "Fide Reemp Internet Up" },
    { label: "Aumentos Plan Pos/Net", claveObj: "aumentos_plan_pos_net", claveRes: "Aumentos", claveIncent: "Aumentos" }
  ];

  const selects = document.querySelectorAll('#employeeSelect, #supervisoreSelect');
  selects.forEach(sel => {
    sel.addEventListener('change', (event) => {
      const selectId = event.target.id;
      const empleadoId = event.target.value;

      let url = `/api/incentivos?empleado_id=${empleadoId}`;

      fetch(url).then(response => {
        if (!response.ok) {
          console.error(`Error HTTP: ${response.status} ${response.statusText}`);
          throw new Error(`Error al cargar los Datos de Incentivos: ${response.status}`);
        }
        return response.json();
      })
        .then(data => {
          const objetivos = data.objetivos || {};
          const resultados = data.resultados || {};
          const incentivo = data.incentivo || {};
          const logros = data.logro || {};
          console.log("Datos recibidos:", data);

          objetivosResultadosTableBody.innerHTML = ''; // limpiar

          mapProductos.forEach(item => {
            const objNum = parseFloat(objetivos[item.claveObj]) || 0;
            const resNum = parseFloat(resultados[item.claveRes]) || 0;
            const incentivoValor = parseFloat(incentivo[item.claveIncent]) || 0;

            // Debug: imprimir valores de cada item
            console.log(`Procesando ${item.label}:`);
            console.log(`- claveObj: ${item.claveObj}, valor: ${objNum}`);
            console.log(`- claveRes: ${item.claveRes}, valor: ${resNum}`);
            console.log(`- claveIncent: ${item.claveIncent}, valor: ${incentivoValor}`);

            // Obtenemos el porcentaje de logro directamente de la API
            // o lo calculamos si no está disponible
            let logro = 0;
            if (logros[item.claveRes]) {
              logro = parseFloat(logros[item.claveRes]);
            } else if (objNum > 0) {
              logro = (resNum / objNum) * 100;
            }

            // Valores para mostrar en las columnas de incentivos
            let incentivo75 = 0;
            let incentivo100 = 0;

            // Determinamos qué columna de incentivo debe mostrar el valor
            // basado en el logro alcanzado
            if (logro >= 100 && incentivoValor > 0) {
              incentivo100 = incentivoValor;
            } else if (logro >= 75 && incentivoValor > 0) {
              incentivo75 = incentivoValor;
            }

            console.log(`${item.label}: logro=${logro}, incentivo=${incentivoValor}, 75%=${incentivo75}, 100%=${incentivo100}`);

            logro = logro.toFixed(2);
            const logroClass = getStatusClass(parseFloat(logro));

            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${item.label}</td>
              <td>${objNum}</td>
              <td>${resNum}</td>
              <td><span class="${logroClass}">${logro}%</span></td> 
              <td>$${incentivo75.toFixed(2)}</td>
              <td>$${incentivo100.toFixed(2)}</td>
            `;

            objetivosResultadosTableBody.appendChild(tr);
          });
        })
        .catch(error => {
          console.error('Error:', error);
          // Mostrar un mensaje de error al usuario
          objetivosResultadosTableBody.innerHTML = `
            <tr>
              <td colspan="6" style="text-align: center; color: red;">
                Error al cargar los datos: ${error.message || 'Error desconocido'}
              </td>
            </tr>
          `;
        });
    });
  });
});