document.addEventListener('DOMContentLoaded', function () {
    const topVentasUrl = "/api/top_ventas";
    const leaderboardGrid = document.querySelector('.leaderboard-grid');

    fetch(topVentasUrl)
        .then(response => response.json())
        .then(data => {
            leaderboardGrid.innerHTML = ''; // Limpiar el contenido existente
            data.forEach((vendedor, index) => {
                const participantCard = document.createElement('div');
                participantCard.classList.add('participant-card');

                participantCard.innerHTML = `
                    <span class="position-number">${index + 1}</span>                    
                    <img src="/static/images/${vendedor.nombre.substring(0,7)}.jpg"
                        onerror="this.src='/static/images/logo.png'" 
                        alt="${vendedor.nombre}" 
                        class="profile-pic">
                    <h3 class="participant-name">${vendedor.nombre.substring(10)}</h3>
                    <p class="participant-points" style="color: #A0E86F;">${vendedor.total_pav}</p>
                    <span class="points-label">PAV</span>
                    <span class="position-change up">↑ +1</span>
                `;
                console.log(vendedor.nombre);
                leaderboardGrid.appendChild(participantCard);
            });
        })
        .catch(error => console.error('Error fetching top ventas:', error));        
});