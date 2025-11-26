document.addEventListener('DOMContentLoaded', function () {
    const btnSubirArchivo = document.getElementById('btnSubirArchivo');
    const inputArchivo = btnSubirArchivo.querySelector('input[type="file"]');
    const loader = document.getElementById('loader');
    const checkboxes = document.querySelectorAll('input[name="upload_type"]');

    function showLoader() {
        loader.style.display = 'flex';
    }

    function hideLoader() {
        loader.style.display = 'none';
    }

    // Asegurarse de que solo un checkbox esté seleccionado a la vez
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            checkboxes.forEach(cb => {
                if (cb !== this) {
                    cb.checked = false;
                }
            });
        });
    });

    inputArchivo.addEventListener('change', function () {
        const file = this.files[0];
        if (!file) {
            return;
        }

        const selectedCheckbox = document.querySelector('input[name="upload_type"]:checked');
        if (!selectedCheckbox) {
            alert('Por favor, seleccione un tipo de archivo para cargar.');
            inputArchivo.value = ''; // Limpiar el input de archivo
            return;
        }

        const uploadType = selectedCheckbox.value;
        let endpoint = '';
        let formDataName = '';
        let expectedHeaders = [];
        let headerRow = 1; // Por defecto, la primera fila
        let startColumn = 'A';

        switch (uploadType) {
            case 'ventas':
                endpoint = '/api/upload_ventas';
                formDataName = 'file';
                expectedHeaders = [
                    'id_compania',
                ];
                headerRow = 10;
                startColumn = 'B';
                break;
            case 'pagos':
                endpoint = '/api/upload_pagos';
                formDataName = 'file';
                expectedHeaders = [
                    'id_tipo_compania',
                ];
                headerRow = 10;
                startColumn = 'B';
                break;
            case 'objetivos':
                endpoint = '/api/upload_objetivos';
                formDataName = 'file';
                expectedHeaders = [
                    'id_empleado', 
                ];
                headerRow = 1;
                startColumn = 'A';
                break;
            default:
                alert('Tipo de carga no válido.');
                inputArchivo.value = '';
                return;
        }

        // Validación de cabeceras del archivo Excel
        const reader = new FileReader();
        reader.onload = function (e) {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });
                const firstSheet = workbook.Sheets[workbook.SheetNames[0]];

                // Extraer la fila de la cabecera
                const header = XLSX.utils.sheet_to_json(firstSheet, {
                    header: 1,
                    range: `${startColumn}${headerRow}` // Empezar a leer desde la celda correcta
                })[0];

                // Filtrar valores nulos o vacíos de la cabecera leída
                const cleanedHeader = header.filter(h => h);

                console.log("Cabecera esperada:", expectedHeaders);
                console.log("Cabecera extraída (cruda):", header);
                console.log("Cabecera extraída (limpia):", cleanedHeader);

                if (JSON.stringify(cleanedHeader) !== JSON.stringify(expectedHeaders)) {
                    alert('Las cabeceras del archivo no coinciden con las esperadas para el tipo de carga seleccionado.');
                    inputArchivo.value = '';
                    return;
                }

                // Si las cabeceras son correctas, proceder con la carga
                const formData = new FormData();
                formData.append(formDataName, file);
                showLoader();

                fetch(endpoint, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    hideLoader();
                    if (data.message) {
                        alert(data.message);
                    } else if (data.error) {
                        alert(`Error al cargar el archivo: ${data.error}`);
                    } else {
                        alert('Respuesta inesperada del servidor.');
                    }
                    inputArchivo.value = ''; // Limpiar el input después de procesar
                })
                .catch(error => {
                    hideLoader();
                    console.error('Error:', error);
                    alert('Ocurrió un error al procesar la solicitud.');
                    inputArchivo.value = ''; // Limpiar el input en caso de error
                });
            } catch (error) {
                console.error("Error al leer el archivo Excel:", error);
                alert("No se pudo leer el archivo. Asegúrese de que sea un archivo Excel válido y que la estructura sea la correcta.");
                inputArchivo.value = '';
            }
        };
        reader.readAsArrayBuffer(file);
    });

    const btnProcesarVentas = document.getElementById('btnProcesarVentas');
    btnProcesarVentas.addEventListener('click', function () {
        showLoader();
        fetch('/api/generar_ventas', {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                hideLoader();
                if (data.status === 'success' || data.status === 'warning') {
                    alert(data.message);
                } else {
                    alert('Error al procesar las ventas: ' + (data.message || data.error));
                }
            })
            .catch(error => {
                hideLoader();
                console.error('Error:', error);
                alert('Ocurrió un error al procesar la solicitud.');
            });
    });

    // Modal Logic
    const modal = document.getElementById("userModal");
    const btnOpen = document.getElementById("btnOpenUserModal");
    const spanClose = document.getElementsByClassName("close")[0];

    if (btnOpen) {
        btnOpen.onclick = function() {
            modal.style.display = "flex";
            // Add class for animation if needed, e.g., modal.classList.add('show');
            setTimeout(() => modal.classList.add('show'), 10);
        }
    }

    if (spanClose) {
        spanClose.onclick = function() {
            modal.classList.remove('show');
            setTimeout(() => modal.style.display = "none", 300);
        }
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.classList.remove('show');
            setTimeout(() => modal.style.display = "none", 300);
        }
    }

    // Crear Usuario Admin
    const createUserForm = document.getElementById('createUserForm');
    if (createUserForm) {
        createUserForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const usuario = document.getElementById('new_usuario').value;
            const codigo_usuario = document.getElementById('new_codigo_usuario').value;
            const nivel = document.getElementById('new_nivel').value;
            const temp_password = document.getElementById('temp_password').value;

            showLoader();

            try {
                const token = localStorage.getItem('token');
                const response = await fetch('/api/admin/create-user', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + token
                    },
                    body: JSON.stringify({
                        usuario,
                        codigo_usuario,
                        nivel,
                        temp_password
                    })
                });

                const data = await response.json();
                hideLoader();

                if (response.ok) {
                    alert(data.msg);
                    createUserForm.reset();
                    // Close modal
                    if (modal) {
                        modal.classList.remove('show');
                        setTimeout(() => modal.style.display = "none", 300);
                    }
                } else {
                    alert(data.msg || "Error al crear usuario");
                }
            } catch (error) {
                hideLoader();
                console.error("Error:", error);
                alert("Error de conexión");
            }
        });
    }
});
// Se necesita la librería xlsx.js para la validación de cabeceras
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.17.0/xlsx.full.min.js';
document.head.appendChild(script);
