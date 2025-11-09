
document.addEventListener('DOMContentLoaded', function () {
    const btnSubirVentas = document.getElementById('btnSubirVentas');
    const inputVentas = btnSubirVentas.querySelector('input[type="file"]');

    inputVentas.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('ventas_excel', file);

            fetch('/api/upload_ventas', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Archivo de ventas cargado y procesado correctamente.');
                } else {
                    alert('Error al cargar el archivo: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ocurrió un error al procesar la solicitud.');
            });
        }
    });
});
