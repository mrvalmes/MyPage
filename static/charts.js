const lineChart = document.getElementById('chartMain');

const dataLine = {
  labels: [
    'Enero',
    'Febrero',
    'Marzo',
    'Abril',
    'Mayo',
    'Junio',
    'Julio',
    'Agosto',
    'Septiembre',
    'Octubre',
    'Noviembre',
    'Diciembre'
  ],
  datasets: [
    {
      label: 'Card',
      data: [22, 48, 41, 53, 82, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(255, 255, 0, 1)',
      borderColor: 'rgba(255, 255, 0, 1)',
      borderWidth: 2
    },
    {
      label: 'Flex',
      data: [65, 92, 53, 114, 72, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(1, 126, 250, 1)',
      borderColor: 'rgba(1, 126, 250, 1)',
      borderWidth: 2
    },
    {
      label: 'Internet',
      data: [49, 111, 102, 49, 58, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(0, 255, 0, 1)',
      borderColor: 'rgba(0, 255, 0, 1)',
      borderWidth: 2
    },
    {
      label: 'Fijos',
      data: [10, 8, 15, 0, 3, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(255, 0, 255, 1)',
      borderColor: 'rgba(255, 0, 255, 1)',
      borderWidth: 2
    },
    {
      label: 'Migra',
      data: [8, 14, 10, 11, 2, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(255, 165, 0, 1)',
      borderColor: 'rgba(255, 165, 0, 1)',
      borderWidth: 2
    },
    {
      label: 'Fide Pos',
      data: [4, 3, 1, 2, 5, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(128, 0, 128, 1)',
      borderColor: 'rgba(128, 0, 128, 1)',
      borderWidth: 2
    },
    {
      label: 'Fide Up',
      data: [16, 7, 30, 9, 8, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(255, 192, 203, 1)',
      borderColor: 'rgba(255, 192, 203, 1)',
      borderWidth: 2
    },
    {
      label: 'Reemp Pos',
      data: [20, 25, 22, 24, 30, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(0, 128, 128, 1)',
      borderColor: 'rgba(0, 128, 128, 1)',
      borderWidth: 2
    },
    {
      label: 'Reemp Up',
      data: [20, 21, 23, 30, 12, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(0, 255, 128, 1)',
      borderColor: 'rgba(0, 255, 128, 1)',
      borderWidth: 2
    },
    {
      label: 'Fide/Reemp Net Up',
      data: [3, 1, 4, 6, 7, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(255, 0, 0, 1)',
      borderColor: 'rgba(255, 0, 0, 1)',
      borderWidth: 2
    },
    {
      label: 'Aumentos',
      data: [100, 54, 66, 70, 55, 0, 0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(0, 0, 255, 1)',
      borderColor: 'rgba(0, 0, 255, 1)',
      borderWidth: 2
    }
  ]
};

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
      max: 200,
      ticks: { stepSize: 50 },
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
          return `${ctx[0].label} 2024`;
        },
        label: ctx => {
          return `${ctx.dataset.label}: ${ctx.raw}`;
        }
      }
    }
  }
};

const annotationLine = {
  id: 'annotationLine',
  beforeDraw: chart => {
    if (chart.tooltip._active && chart.tooltip._active.length) {
      const ctx = chart.ctx;
      ctx.save();
      const activePoint = chart.tooltip._active[0];
      const display = lineChart.getContext('2d');

      const gradient = display.createLinearGradient(0, 0, 0, 330);

      gradient.addColorStop(0, 'rgba(37, 75, 209, 0)');
      gradient.addColorStop(1, 'rgba(37, 75, 209, 0.1)');

      ctx.beginPath();
      ctx.moveTo(activePoint.element.x, chart.chartArea.top);
      ctx.lineTo(activePoint.element.x, chart.chartArea.bottom);
      ctx.lineWidth = 40;
      ctx.strokeStyle = gradient;
      ctx.strokeRect(activePoint.element.x, chart.chartArea.top, 0, 282);
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
      ctx.lineWidth = 1;
      ctx.strokeStyle = 'rgba(1, 126, 250, 0.8)';
      ctx.stroke();
      ctx.restore();
    }
  }
};

const configLine = {
  type: 'line',
  data: dataLine,
  options: genericOptions,
  plugins: [annotationLine, lineDash]
};

const chartMain = new Chart(lineChart, configLine);

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
      });
    }

    chartMain.update();
  });
});