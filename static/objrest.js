document.addEventListener('DOMContentLoaded', () => {
  const objetivosResultadosTableBody = document.querySelector('#obj-rest table tbody');

  if (!objetivosResultadosTableBody) {
    console.error("No se encontró el tbody de la tabla de objrest.");
    return;
  }

  // Función para mostrar órdenes según la persona seleccionada
  function mostrarOrdenes(data, personID) {
    objetivosResultadosTableBody.innerHTML = ''; // Limpiar resultados anteriores

    const personaSeleccionada = data.find(person => person.personID === personID);

    // Si hay una persona seleccionada, mostrar sus órdenes; de lo contrario, mostrar todas las órdenes
    const ordenesParaMostrar = personaSeleccionada ? personaSeleccionada.orders : data.flatMap(person => person.orders);

    ordenesParaMostrar.forEach(order => {
      const tr = document.createElement('tr');
      let statusClass = '';
      let statusClassPro = '';

      const status = parseFloat(order.status);
      const statuspro = parseFloat(order.productProyect);

      // Determinar la clase de estado
      if (status < 74) {
        statusClass = 'danger';
      } else if (status >= 75 && status <= 99) {
        statusClass = 'warning';
      } else {
        statusClass = 'success';
      }

      if (statuspro < 74) {
        statusClassPro = 'danger';
      } else if (statuspro >= 75 && statuspro <= 99) {
        statusClassPro = 'warning';
      } else {
        statusClassPro = 'success';
      }

      const trContent = `
                <td>${order.productName}</td>
                <td>${order.productObj}</td>
                <td>${order.productStatus}</td>
                <td class="${statusClass}">${order.status}%</td>
                <td class="${statusClassPro}">${order.productProyect}%</td>
            `;
      tr.innerHTML = trContent;
      objetivosResultadosTableBody.appendChild(tr);
    });
  }

  // Cargar datos desde el archivo JSON
  fetch('json/ventas.json')
    .then(response => {
      if (!response.ok) {
        throw new Error('Error al cargar el archivo JSON');
      }
      return response.json();
    })
    .then(data => {
      // Agregar un listener para la selección de personas
      document.querySelector('#personSelect').addEventListener('change', (event) => {
        const selectedPersonID = parseInt(event.target.value);
        mostrarOrdenes(data, selectedPersonID);
      });

      // Llamar a mostrarOrdenes sin argumento para mostrar resultados generales inicialmente
      mostrarOrdenes(data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
});