document.addEventListener('DOMContentLoaded', () => {

  // Seleccionar los elementos tbody ordenes
  const ordenesTableBody = document.querySelector('#ordenes table tbody');

  if (!ordenesTableBody) {
    console.error("No se encontró el tbody de la tabla de órdenes.");
    return;
  }

  // Cargar las órdenes desde el archivo JSON
  fetch('json/ordenes.json')
    .then(response => {
      if (!response.ok) {
        throw new Error('Error al cargar el datos');
      }
      return response.json();
    })
    .then(ordenVenta => {
      // Llenar la tabla de "Ordenes"
      ordenVenta.forEach(orderV => {
        const tr = document.createElement('tr');
        const trContent = `
                    <td>${orderV.ordenId}</td>
                    <td>${orderV.fechaDigitado}</td>
                    <td>${orderV.fechaTermino}</td>
                    <td>${orderV.tipoTransaccion}</td>
                    <td>${orderV.cliente}</td>
                    <td>${orderV.numActivado}</td>
                `;
        tr.innerHTML = trContent;
        ordenesTableBody.appendChild(tr);
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
});