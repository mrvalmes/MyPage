document.addEventListener('DOMContentLoaded', () => {
  const objetivosResultadosTableBody = document.querySelector('#incentivo table tbody');
  if (!objetivosResultadosTableBody) {
    console.error("No se encontró el <tbody> de la tabla incentivo.");
    return;
  }
  let objetivosResultadosTableFoot = document.querySelector('#incentivo table tfoot');
  if (!objetivosResultadosTableFoot) {
    objetivosResultadosTableFoot = document.createElement('tfoot');
    document.querySelector('#incentivo table').appendChild(objetivosResultadosTableFoot);
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
          //console.log("Datos recibidos:", data);

          objetivosResultadosTableBody.innerHTML = ''; // limpiar

          let totalIncentivo75 = 0;
          let totalIncentivo100 = 0;

          mapProductos.forEach(item => {
            const objNum = parseFloat(objetivos[item.claveObj]) || 0;
            const resNum = parseFloat(resultados[item.claveRes]) || 0;
            const incentivoValor = parseFloat(incentivo[item.claveIncent]) || 0;

            // Debug: imprimir valores de cada item
           /* console.log(`Procesando ${item.label}:`);
            console.log(`- claveObj: ${item.claveObj}, valor: ${objNum}`);
            console.log(`- claveRes: ${item.claveRes}, valor: ${resNum}`);
            console.log(`- claveIncent: ${item.claveIncent}, valor: ${incentivoValor}`);*/

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

            totalIncentivo75 += incentivo75;
            totalIncentivo100 += incentivo100;

            //console.log(`${item.label}: logro=${logro}, incentivo=${incentivoValor}, 75%=${incentivo75}, 100%=${incentivo100}`);

            logro = logro.toFixed(2);
            const logroClass = getStatusClass(parseFloat(logro));

            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${item.label}</td>
              <td>${objNum}</td>
              <td>${resNum}</td>
              <td><span class="${logroClass}">${logro}%</span></td> 
              <td>$${incentivo75.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
              <td>$${incentivo100.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
            `;

            objetivosResultadosTableBody.appendChild(tr);
          });

          objetivosResultadosTableFoot.innerHTML = ''; // limpiar
          const totalRow = document.createElement('tr');
          totalRow.innerHTML = `
            <td colspan="4" style="text-align: right;"><strong>Total:</strong></td>
            <td><strong>  </strong></td>
            <td><strong>  </strong></td>
            <td><strong>  </strong></td>
            <td><strong>$${totalIncentivo75.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></td>
            <td><strong>$${totalIncentivo100.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></td>            
          `;
          objetivosResultadosTableFoot.appendChild(totalRow);
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