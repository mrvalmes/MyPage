document.addEventListener('DOMContentLoaded', function () {
    const topVentasUrl = "/api/top_ventas";
    const oldPositionsUrl = "/static/data/positions.json";
    const leaderboardGrid = document.querySelector('.leaderboard-grid');

    // Update date
    const dateElement = document.getElementById('current-date');
    const today = new Date();
    const monthNames = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
    const formattedDate = `${today.getDate()} de ${monthNames[today.getMonth()]} de ${today.getFullYear()}`;
    dateElement.textContent = formattedDate;

    Promise.all([fetch(topVentasUrl), fetch(oldPositionsUrl)])
        .then(responses => Promise.all(responses.map(res => res.json())))
        .then(([newData, oldData]) => {
            const oldPositions = new Map(oldData.map((vendedor, index) => [vendedor.nombre, index + 1]));
            leaderboardGrid.innerHTML = ''; // Limpiar el contenido existente

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

            // Update positions on the server
            fetch('/api/update_positions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newData),
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});