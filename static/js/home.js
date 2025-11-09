document.addEventListener('DOMContentLoaded', function () {

    function fetchRecentActivity() {
        fetch('/api/recent-activity')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                const recentActivityList = document.querySelector('.orders ul');
                if (recentActivityList) {
                    recentActivityList.innerHTML = ''; // Limpiar lista existente
                    if (data && data.length > 0) {
                        data.forEach(activity => {
                            const listItem = document.createElement('li');
                            listItem.classList.add('task-list');
                            
                            const taskTitle = document.createElement('div');
                            taskTitle.classList.add('task-title');
                            
                            const paragraph = document.createElement('p');                            
                            paragraph.textContent = `${activity[0]}: ${activity[1]}`;
                            
                            taskTitle.appendChild(paragraph);
                            listItem.appendChild(taskTitle);
                            recentActivityList.appendChild(listItem);
                        });
                    } else {
                        recentActivityList.innerHTML = '<li class="task-list"><div class="task-title"><p>No hay actividad reciente.</p></div></li>';
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching recent activity:', error);
                const recentActivityList = document.querySelector('.orders ul');
                if (recentActivityList) {
                    recentActivityList.innerHTML = '<li class="task-list"><div class="task-title"><p>Error al cargar la actividad.</p></div></li>';
                }
            });
    }

    let salesChart = null; // variable global

    function fetchSalesOverview() {
        fetch('/api/sales-overview')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(salesOverviewData => {
                const ctx = document.getElementById('salesOverviewChart').getContext('2d');

                if (salesChart) {
                    salesChart.destroy();
                }

                if (!salesOverviewData || !salesOverviewData.data || salesOverviewData.data.length === 0) {
                    console.warn("Sin datos para el gráfico de Overview.");
                    return;
                }

                salesChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: salesOverviewData.labels,
                        datasets: [{
                            label: 'Sales Overview',
                            data: salesOverviewData.data,
                            backgroundColor: [
                                '#FF6384',
                                '#36A2EB',
                                '#FFCE56',
                                '#4BC0C0',
                                '#A236EB',
                                '#FF9F40'
                            ],
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,                        
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.label || '';
                                        if (label) label += ': ';
                                        if (context.parsed !== null) {
                                            label += context.parsed.toFixed(2) + '%';
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => console.error('Error fetching sales overview:', error));
    }

    fetchRecentActivity();
    fetchSalesOverview();
});
