document.addEventListener('DOMContentLoaded', () => {
  const btnBuscar = document.getElementById('btnBuscar');
  const selectSupervisor = document.getElementById('supervisoreSelect');
  const dateInput = document.querySelector('#conversion-rate input[type="date"]');
  const tbody = document.querySelector('#conversion-rate tbody');

  // Comprobaciones básicas
  if (!btnBuscar) {
    console.error("No se encontró #btnBuscar. Verifica que el elemento exista y su id sea correcto.");
    return;
  }
  if (!selectSupervisor) {
    console.error("No se encontró #supervisoreSelect. Verifica que el select tenga ese id.");
  }
  if (!dateInput) {
    console.error("No se encontró el input[type='date'] dentro de #conversion-rate.");
  }
  if (!tbody) {
    console.error("No se encontró el <tbody> de la tabla de conversion-rate.");
  }

  // Aseguramos que el icono parezca y se comporte como botón
  btnBuscar.style.cursor = 'pointer';
  btnBuscar.setAttribute('role', 'button');
  btnBuscar.setAttribute('tabindex', '0');

  // Helper para escapar HTML (seguridad)
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str).replace(/[&<>"']/g, s => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[s]);
  }

  async function cargarConversionRate() {
    const supervisor = selectSupervisor ? selectSupervisor.value.trim() : '';
    const dia = dateInput ? dateInput.value.trim() : '';

    if (!supervisor) {
      alert('Seleccione un supervisor');
      if (selectSupervisor) selectSupervisor.focus();
      return;
    }
    if (!dia) {
      alert('Seleccione una fecha');
      if (dateInput) dateInput.focus();
      return;
    }

    const url = `/api/conversion-rate?empleado_id=${encodeURIComponent(supervisor)}&dia=${encodeURIComponent(dia)}`;
    console.log('Solicitando datos CR:', url);

    // Opcional: muestra fila de "cargando"
    if (tbody) tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">Cargando...</td></tr>';

    try {
      const res = await fetch(url, { method: 'GET' });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const data = await res.json();

      if (!Array.isArray(data) || data.length === 0) {
        if (tbody) tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">No hay datos</td></tr>';
        return;
      }

      // Llenar tabla
      if (tbody) tbody.innerHTML = '';
      let totalVentas = 0;
      let totalPagos = 0;

      data.forEach(row => {
        const ventas = parseFloat(row.ventas_count) || 0;
        const pagos = parseFloat(row.pagos_count) || 0;
        
        totalVentas += ventas;
        totalPagos += pagos;

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${escapeHtml(row.usuario_creo_orden.substring(10))}</td>
          <td>${escapeHtml(ventas)}</td>
          <td>${escapeHtml(pagos)}</td>
          <td>${escapeHtml(row.conversion_rate_pct)}%</td>
        `;
        tbody.appendChild(tr);
      });

      // Calcular CR General
      const crGeneral = totalPagos > 0 ? ((totalVentas / totalPagos) * 100).toFixed(2) : 0;

      // Crear y agregar fila de totales
      const totalRow = document.createElement('tr');
      totalRow.style.fontWeight = 'bold';
      totalRow.style.backgroundColor = 'var(--grey)';
      totalRow.innerHTML = `
        <td>Totales</td>
        <td>${totalVentas}</td>
        <td>${totalPagos}</td>
        <td>${crGeneral}%</td>
      `;
      tbody.appendChild(totalRow);

    } catch (err) {
      console.error('Error al cargar Conversion Rate:', err);
      if (tbody) tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:red">Error al obtener datos</td></tr>';
      alert('Ocurrió un error al cargar los datos. Revisa la consola (F12) para más detalles.');
    }
  }

  // Click y accesibilidad por teclado (Enter / Space)
  btnBuscar.addEventListener('click', cargarConversionRate);
  btnBuscar.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      cargarConversionRate();
    }
  });

  // También permitir Enter en el dateInput para buscar rápidamente
  if (dateInput) {
    dateInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') cargarConversionRate();
    });
  }

  // Inicializa fecha con hoy si está vacío (opcional)
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().split('T')[0];
  }
});
