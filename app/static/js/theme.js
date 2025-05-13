// static/js/theme.js
document.addEventListener('DOMContentLoaded', () => {
    const themeSwitch = document.getElementById('checkbox');
    const themeStyle = document.getElementById('theme-style');
    const html = document.documentElement;
    
    // Controlla il tema salvato
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Applica il tema salvato
    if (savedTheme === 'dark') {
        enableDarkMode();
    } else {
        enableLightMode();
    }
    
    // Gestisci il cambio tema
    themeSwitch.addEventListener('change', toggleTheme);
    
    // Toggle sidebar su mobile
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('active');
        });
    }

    // Funzioni per gestire il tema
    function toggleTheme() {
        if (themeSwitch.checked) {
            enableDarkMode();
        } else {
            enableLightMode();
        }
        updateChartsTheme();
    }
    
    function enableDarkMode() {
        themeStyle.href = '/static/css/dark.css';
        localStorage.setItem('theme', 'dark');
        html.className = 'dark-theme';
        themeSwitch.checked = true;
        
        // Aggiorna i colori dei grafici per il tema scuro
        if (typeof Chart !== 'undefined') {
            Chart.defaults.color = '#adb5bd';
            Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
        }
    }
    
    function enableLightMode() {
        themeStyle.href = '/static/css/light.css';
        localStorage.setItem('theme', 'light');
        html.className = 'light-theme';
        themeSwitch.checked = false;
        
        // Ripristina i colori dei grafici per il tema chiaro
        if (typeof Chart !== 'undefined') {
            Chart.defaults.color = '#6c757d';
            Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.05)';
        }
    }
    
    function updateChartsTheme() {
        // Ri-crea i grafici con i nuovi colori
        if (typeof weeklyChart !== 'undefined' && weeklyChart) {
            weeklyChart.destroy();
            const weeklyData = weeklyChart.data;
            const ctx = document.getElementById('weeklyChart').getContext('2d');
            weeklyChart = new Chart(ctx, {
                type: 'bar',
                data: weeklyData,
                options: getChartOptions('Andamento settimanale')
            });
        }
        
        if (typeof userChart !== 'undefined' && userChart) {
            userChart.destroy();
            const userData = userChart.data;
            const ctx = document.getElementById('userChart').getContext('2d');
            userChart = new Chart(ctx, {
                type: 'doughnut',
                data: userData,
                options: getChartOptions('Distribuzione per utente', true)
            });
        }
    }

    // Funzione per ottenere le opzioni dei grafici (allineata con main.js)
    function getChartOptions(title, isDoughnut = false) {
        const textColor = html.classList.contains('dark-theme') ? '#adb5bd' : '#6c757d';
        const gridColor = html.classList.contains('dark-theme') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)';
        
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: isDoughnut ? 'right' : 'top',
                    labels: {
                        color: textColor,
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: html.classList.contains('dark-theme') ? 'rgba(40, 40, 40, 0.9)' : 'rgba(30, 30, 30, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#f8f9fa',
                    titleFont: { size: 14 },
                    bodyFont: { size: 12 },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true,
                    borderWidth: 0
                }
            },
            scales: isDoughnut ? {} : {
                x: {
                    grid: { 
                        display: false,
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            },
            cutout: isDoughnut ? '70%' : undefined,
            animation: {
                duration: animationDuration
            }
        };
    }
});