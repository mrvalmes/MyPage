document.addEventListener('DOMContentLoaded', function () {
    const leaderboardGrid = document.querySelector('.leaderboard-grid');
    const dateElement = document.getElementById('current-date');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const btnBuscar = document.getElementById('btnBuscar');

    function updateLeaderboard(startDate, endDate) {
        let topVentasUrl = "/api/top_ventas";
        if (startDate && endDate) {
            topVentasUrl += `?start_date=${startDate}&end_date=${endDate}`;
        } else if (startDate) {
            topVentasUrl += `?start_date=${startDate}`;
        } else if (endDate) {
            topVentasUrl += `?end_date=${endDate}`;
        }

        const oldPositionsUrl = "/static/data/positions.json";

        // Update date display
        const displayDate = startDate ? new Date(startDate + 'T00:00:00') : new Date();
        const monthNames = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
        const formattedDate = `${displayDate.getDate()} de ${monthNames[displayDate.getMonth()]} de ${displayDate.getFullYear()}`;
        dateElement.textContent = formattedDate;

        Promise.all([fetch(topVentasUrl), fetch(oldPositionsUrl)])
            .then(responses => Promise.all(responses.map(res => res.json())))
            .then(([newData, oldData]) => {
                const oldPositions = new Map(oldData.map((vendedor, index) => [vendedor.nombre, index + 1]));
                leaderboardGrid.innerHTML = ''; // Limpiar el contenido existente

                if (newData.length === 0) {
                    leaderboardGrid.innerHTML = '<p>No hay datos para la fecha seleccionada.</p>';
                    return;
                }

                newData.forEach((vendedor, index) => {
                    const newPosition = index + 1;
                    const oldPosition = oldPositions.get(vendedor.nombre);
                    let positionChangeHtml = '<span class="position-change">-</span>';

                    if (oldPosition) {
                        const change = oldPosition - newPosition;
                        if (change > 0) {
                            positionChangeHtml = `<span class="position-change up">↑ +${change}</span>`;
                        } else if (change < 0) {
                            positionChangeHtml = `<span class="position-change down">↓ ${change}</span>`;
                        }
                    }

                    const participantCard = document.createElement('div');
                    participantCard.classList.add('participant-card');

                    participantCard.innerHTML = `
                        <span class="position-number">${newPosition}</span>
                        <img src="/static/images/${vendedor.nombre.substring(0, 7)}.jpg"
                            onerror="this.src='/static/images/logo.png'"
                            alt="${vendedor.nombre}"
                            class="profile-pic">
                        <h3 class="participant-name">${vendedor.nombre.substring(10)}</h3>
                        <p class="participant-points" style="color: #A0E86F;">${vendedor.total_pav}</p>
                        <span class="points-label">PAV</span>
                        ${positionChangeHtml}
                    `;
                    leaderboardGrid.appendChild(participantCard);
                });

                // Update positions on the server only if we are looking at the current month
                if (!startDate && !endDate) {
                    fetch('/api/update_positions', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(newData),
                    });
                }
            })
            .catch(error => console.error('Error fetching data:', error));
    }

    // Initial load
    updateLeaderboard();

    // Event listener for search button
    btnBuscar.addEventListener('click', function() {
        updateLeaderboard(startDateInput.value, endDateInput.value);
    });
});