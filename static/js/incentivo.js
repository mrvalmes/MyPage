document.addEventListener('DOMContentLoaded', () => {
  const objetivosResultadosTableBody = document.querySelector('#incentivo table tbody');
  const employeeSelect = document.getElementById('employeeSelect'); 
  const btnBuscar = document.getElementById('btnBuscar');
  const monthSelect = document.getElementById('MonthSelect');
  const yearSelect = document.getElementById('YearSelect');

  if (!objetivosResultadosTableBody) {
    console.error("No se encontró el <tbody> de la tabla incentivo.");
    return;
  }
  let objetivosResultadosTableFoot = document.querySelector('#incentivo table tfoot');
  if (!objetivosResultadosTableFoot) {
    objetivosResultadosTableFoot = document.createElement('tfoot');
    document.querySelector('#incentivo table').appendChild(objetivosResultadosTableFoot);
  }

  // Función para poblar el dropdown de empleados
  function populateEmployees() {
    fetch('/api/empleados')
      .then(response => response.json())
      .then(data => {
        data.forEach(employee => {
          const option = document.createElement('option');
          option.value = employee.id;
          option.textContent = employee.nombre;
          employeeSelect.appendChild(option);
        });
      })
      .catch(error => console.error('Error fetching employees:', error));
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

    function fetchAndDisplayData() {

      const empleadoId = employeeSelect.value;
      const selectedMonth = monthSelect.value;
      const selectedYear = yearSelect.value;     

      let url = `/api/incentivos?empleado_id=${empleadoId}`;
      if (selectedMonth) {
        url += `&month=${selectedMonth}`;
      }
      if (selectedYear) {
        url += `&year=${selectedYear}`;
      }  

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

        objetivosResultadosTableBody.innerHTML = ''; // limpiar

        let totalIncentivo75 = 0;
        let totalIncentivo100 = 0;
        let totalTotales = 0;
        let totalObjetivos = 0;
        let totalResultados = 0;
        let totalPorcentaje = 0;


        mapProductos.forEach(item => {
          const objNum = parseFloat(objetivos[item.claveObj]) || 0;
          const resNum = parseFloat(resultados[item.claveRes]) || 0;
          const incentivoValor = parseFloat(incentivo[item.claveIncent]) || 0;

          let logro = 0;
          if (logros[item.claveRes]) {
            logro = parseFloat(logros[item.claveRes]);
          } else if (objNum > 0) {
            logro = (resNum / objNum) * 100;
          }

          let incentivo75 = 0;
          let incentivo100 = 0;

          if (logro >= 100 && incentivoValor > 0) {
            incentivo100 = incentivoValor;
          } else if (logro >= 75 && incentivoValor > 0) {
            incentivo75 = incentivoValor;
          }

          const totales = incentivo75 + incentivo100;
          totalIncentivo75 += incentivo75;
          totalIncentivo100 += incentivo100;
          totalTotales += totales;
          totalObjetivos += objNum;
          totalResultados += resNum;
          totalPorcentaje = totalResultados / totalObjetivos * 100 || 0;

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
            <td>$${totales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
          `;

          objetivosResultadosTableBody.appendChild(tr);
        });

        const logroClass = getStatusClass(parseFloat(totalPorcentaje));

        objetivosResultadosTableFoot.innerHTML = ''; // limpiar
        const totalRow = document.createElement('tr');
        totalRow.innerHTML = `
          <td colspan="4" style="text-align: right;"><strong>Totales:</strong></td>
          <td>${totalObjetivos}</td>
          <td>${totalResultados}</td>
          <td><span class="${logroClass}">${totalPorcentaje.toFixed(2)}%</span></td>
          <td><strong>$${totalIncentivo75.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></td>
          <td><strong>$${totalIncentivo100.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></td>
          <td><strong>$${totalTotales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></td>
        `;
        objetivosResultadosTableFoot.appendChild(totalRow);
      })
      .catch(error => {
        console.error('Error:', error);
        objetivosResultadosTableBody.innerHTML = `
          <tr>
            <td colspan="7" style="text-align: center; color: red;">
              Error al cargar los datos: ${error.message || 'Error desconocido'}
            </td>
          </tr>
        `;
      });
  }

  // Llenar el dropdown de empleados al cargar la página
  populateEmployees();

  btnBuscar.addEventListener('click', fetchAndDisplayData);  
});