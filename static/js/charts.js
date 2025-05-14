//Inicio cargar el chart lineal
//Variable global para la gráfica (para luego manipularla en filtros)
let chartMain = null;
let showPercentage = false;
//Buscar la referencia al <canvas id="chartMain">
const lineChart = document.getElementById('chartMain');
function actualizarEscala() {
  const nuevoMax = parseInt(document.getElementById('maxInput').value, 10) || 85;
  const nuevoStep = parseInt(document.getElementById('stepInput').value, 10) || 5;

  chartMain.options.scales.y.max = nuevoMax;
  chartMain.options.scales.y.ticks.stepSize = nuevoStep;
  chartMain.update();
}

//opciones genéricas
const genericOptions = {
  responsive: true,
  hoverBackgroundColor: 'white',
  hoverRadius: 7,
  hoverBorderWidth: 3,
  onHover: { mode: ['dataset', 'tooltip'] },
  scales: {
    x: { grid: { display: false } },
    y: {
      min: 0,
      max: 50,
      ticks: { stepSize: 5 },
      grid: { borderDash: [5, 5] }
    }
  },
  layout: {
    padding: {
      bottom: 10,
      left: 15,
      right: 25
    }
  },
  interaction: {
    mode: 'index',
    intersect: false
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      padding: 16,
      titleFont: {
        family: "'Poppins', 'sans-serif'",
        size: 16,
        weight: 'normal'
      },
      backgroundColor: 'rgba(8, 26, 81, 1)',
      bodyColor: 'rgba(255, 255, 255, 0.7)',
      bodyFont: {
        family: "'Poppins', 'sans-serif'",
        size: 15
      },
      bodySpacing: 8,
      boxHeight: 6,
      boxPadding: 8,
      usePointStyle: true,
      callbacks: {
        title: ctx => {
          return `${ctx[0].label}`;
        },
        label: ctx => {
          return `${ctx.dataset.label}: ${ctx.raw}${showPercentage ? ' %' : ''}`;
        }
      }
    }
  }
};

//plugins de anotación
const annotationLine = {
  id: 'annotationLine',
  beforeDraw: chart => {
    if (chart.tooltip._active && chart.tooltip._active.length) {
      const ctx = chart.ctx;
      ctx.save();
      const activePoint = chart.tooltip._active[0];
      const display = lineChart.getContext('2d');

      const gradient = display.createLinearGradient(0, 0, 0, 330);
      gradient.addColorStop(0, 'rgba(41, 233, 16, 0)');
      gradient.addColorStop(1, 'rgba(37, 75, 209, 0.1)');

      ctx.beginPath();
      ctx.moveTo(activePoint.element.x, chart.chartArea.top);
      ctx.lineTo(activePoint.element.x, chart.chartArea.bottom);
      ctx.lineWidth = 60;
      ctx.strokeStyle = gradient;
      ctx.strokeRect(activePoint.element.x, chart.chartArea.top, 0, 430);
      ctx.restore();
    }
  }
};

const lineDash = {
  id: 'lineDash',
  beforeDraw: chart => {
    if (chart.tooltip._active && chart.tooltip._active.length) {
      const ctx = chart.ctx;
      ctx.save();
      const activePoint = chart.tooltip._active[0];
      ctx.beginPath();
      ctx.setLineDash([5, 5]);
      ctx.moveTo(activePoint.element.x, chart.chartArea.top);
      ctx.lineTo(activePoint.element.x, chart.chartArea.bottom);
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = 'rgba(1, 126, 250, 0.8)';
      ctx.stroke();
      ctx.restore();
    }
  }
};

function fetchAndRenderChart() {
  const employeeSelect = document.getElementById('employeeSelect');
  const supervisoreSelect = document.getElementById('supervisoreSelect');
  const mode = document.getElementById('modeSelect').value;
  const year = document.getElementById('yearSelect').value;

  let empleadoId = employeeSelect.value;
  let supervisorId = supervisoreSelect.value;

  let id = '';

  let url = `/chart-data?anio=${encodeURIComponent(year)}`;

  // Limpiar el otro selector cuando uno es seleccionado
  if (supervisorId && supervisorId !== "None") {
    employeeSelect.value = "None"; // Limpiar la selección de empleado
    url += `&supervisor=${encodeURIComponent(supervisorId)}&modo=${mode}`;    
    id = supervisorId;

  } else if (empleadoId && empleadoId !== "None") {
    supervisoreSelect.value = "None"; // Limpiar la selección de supervisor
    url += `&empleado=${encodeURIComponent(empleadoId)}&modo=${mode}`;    
    id = empleadoId; 

  } else {
    // Manejar el caso en que ambos son "None"
    url += `&empleado=None`;
  }

  if (mode == 'logro') {
    showPercentage = true;
  } else {
    showPercentage = false;
  }

  fetch(url)
    .then(response => response.json())
    .then(dataLine => {
      if (chartMain) {
        chartMain.destroy();
      }

      if (mode === "logro" && id !== "None") {
        genericOptions.scales.y.min = 0;
        genericOptions.scales.y.max = 150;
        genericOptions.scales.y.ticks.stepSize = 10;
      } else if (mode === "resultados") {
        if (id === "None") {
          genericOptions.scales.y.min = 0;
          genericOptions.scales.y.max = 500;
          genericOptions.scales.y.ticks.stepSize = 5;
        } else {
          genericOptions.scales.y.min = 0;
          genericOptions.scales.y.max = 85;
          genericOptions.scales.y.ticks.stepSize = 5;
        }
      }

      const configLine = {
        type: 'line',
        data: dataLine,
        options: genericOptions,
        plugins: [annotationLine, lineDash]
      };

      chartMain = new Chart(lineChart, configLine);

      // Añadir event listeners a los filtros
      const filters = document.querySelectorAll('.filter');

      filters.forEach(filter => {
        filter.addEventListener('click', () => {
          // Remover la clase 'selected' de todos los filtros
          filters.forEach(f => f.classList.remove('selected'));

          // Agregar la clase 'selected' al filtro clicado
          filter.classList.add('selected');

          // Obtener el label del filtro seleccionado
          const selectedLabel = filter.getAttribute('data-label');

          if (selectedLabel === 'Todos') {
            // Mostrar todos los datasets
            chartMain.data.datasets.forEach(dataset => {
              dataset.hidden = false;
            });
          } else {
            // Filtrar los datasets para mostrar solo el seleccionado
            chartMain.data.datasets.forEach(dataset => {
              dataset.hidden = dataset.label !== selectedLabel;
              genericOptions.scales.y.max = dataset.value; // Escalar grafico al valor maximo del filtro seleccionado.              
            });
          }
          chartMain.update();
        });
      });
    })  
    .catch(error => console.error("Error al cargar datos del gráfico:", error));
}
// Escuchar el evento 'change' en <select> para actualizar el gráfico
document.getElementById('yearSelect').addEventListener('change', fetchAndRenderChart);
document.getElementById('modeSelect').addEventListener('change', fetchAndRenderChart);
document.getElementById('employeeSelect').addEventListener('change', fetchAndRenderChart);
document.getElementById('supervisoreSelect').addEventListener('change', fetchAndRenderChart);
// Llamar una vez para inicializar
fetchAndRenderChart();
