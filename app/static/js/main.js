// Configurazione globale di Chart.js
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#6c757d';
Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.05)';

// Variabili globali
let weeklyChart, userChart;
const animationDuration = 800;

// Funzione principale
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Configura toggle sidebar per mobile
        document.querySelector('.sidebar-toggle').addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('active');
        });

        // Carica i dati iniziali
        await loadData();
        
        // Configura pulsante refresh
        if(document.getElementById('refreshBtn') != null){
            document.getElementById('refreshBtn').addEventListener('click', loadData);
        }
        
        // Auto-refresh ogni 30 secondi
        const refreshInterval = setInterval(loadData, 30000);
        
        // Pulizia all'unload
        window.addEventListener('beforeunload', () => {
            clearInterval(refreshInterval);
        });
        
    } catch (error) {
        console.error('Errore iniziale:', error);
        showError('Errore nel caricamento iniziale');
    }

    // Rimuove automaticamente i messaggi flash dopo 5s
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(el => el.remove());
    }, 5000);
});

// ========== FUNZIONI PRINCIPALI ========== //
async function loadData() {
    try {
        showLoadingState();
        
        // Chiamata API reale
        const { data } = await axios.get('/api/accessi');
        
        // Aggiorna l'interfaccia
        updateStats(data.stats, data.oggi_stats);
        updateCharts(data);
        updateLastUpdated(data.last_updated);
        updateRecentAccess(data.accessi_recenti);

    } catch (error) {
        console.error('Errore nel caricamento:', error);
        showError('Errore nel recupero dati: ' + (error.response?.data?.error || error.message));
    } finally {
        hideLoadingState();
    }
}

// ========== FUNZIONI DI SUPPORTO ========== //
function showLoadingState() {
    // Mostra spinner nelle cards
    document.querySelectorAll('.stat-card p').forEach(el => {
        if (!el.textContent.match(/^\d+$/)) {
            el.innerHTML = '<div class="spinner"></div>';
        }
    });
    
    // Mostra spinner nelle tabelle
    if (document.querySelector('#recentAccessTable tbody')) {
        document.querySelector('#recentAccessTable tbody').innerHTML = `
            <tr>
                <td colspan="3" class="loading-table">
                    <div class="spinner"></div>
                    <span>Caricamento dati...</span>
                </td>
            </tr>
        `;
    }
}

function hideLoadingState() {
    // Nascondi tutti gli spinner
    document.querySelectorAll('.spinner').forEach(el => {
        if (el.parentElement.tagName !== 'TD') {
            el.remove();
        }
    });
}

function updateStats(stats, oggiStats) {
    animateValue('total-access', stats.totali);
    animateValue('success-access', stats.riusciti);
    animateValue('failed-access', stats.falliti);
    animateValue('today-access', oggiStats.oggi_totali);
}

function animateValue(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return; // Se l'elemento non esiste, esci dalla funzione
    const currentValue = parseInt(element.textContent) || 0;

    const duration = animationDuration;
    const startTime = performance.now();
    
    function updateValue(timestamp) {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const value = Math.floor(progress * (targetValue - currentValue) + currentValue);
        
        element.textContent = value;
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        } else {
            element.classList.add('value-loaded');
        }
    }
    
    requestAnimationFrame(updateValue);
}

function updateCharts(data) {
    // Grafico settimanale
    renderWeeklyChart(data.accessi_settimanali);
    
    // Grafico utenti
    renderUserChart(data.accessi_per_utente);
}

function renderWeeklyChart(data) {
    if (!data || data.length === 0) return; // Se non ci sono dati, esci dalla funzione
    if (document.getElementById('weeklyChart') == null) return; // Se l'elemento non esiste, esci dalla funzione
    const ctx = document.getElementById('weeklyChart').getContext('2d');
    
    if (weeklyChart) weeklyChart.destroy();
    
    weeklyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => new Date(item.giorno).toLocaleDateString('it-IT', { 
                weekday: 'short', 
                day: 'numeric' 
            })),
            datasets: [
                {
                    label: 'Riusciti',
                    data: data.map(item => item.riusciti),
                    backgroundColor: 'rgba(6, 214, 160, 0.7)',
                    borderRadius: 6,
                    borderWidth: 0
                },
                {
                    label: 'Falliti',
                    data: data.map(item => item.falliti),
                    backgroundColor: 'rgba(239, 71, 111, 0.7)',
                    borderRadius: 6,
                    borderWidth: 0
                }
            ]
        },
        options: getChartOptions('Andamento settimanale')
    });
}

function renderUserChart(data) {
    if (!data || data.length === 0) return; // Se non ci sono dati, esci dalla funzione
    if (!document.getElementById('userChart')) return;
    const ctx = document.getElementById('userChart').getContext('2d');
    
    if (userChart) userChart.destroy();
    
    userChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.username),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: [
                    'rgba(58, 134, 255, 0.8)',
                    'rgba(6, 214, 160, 0.8)',
                    'rgba(239, 71, 111, 0.8)',
                    'rgba(255, 209, 102, 0.8)',
                    'rgba(17, 159, 216, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: getChartOptions('Distribuzione per utente', true)
    });
}

function getChartOptions(title, isDoughnut = false) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: isDoughnut ? 'right' : 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20
                }
            },
            tooltip: {
                backgroundColor: 'rgba(30, 30, 30, 0.9)',
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
                grid: { display: false }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            }
        },
        cutout: isDoughnut ? '70%' : undefined,
        animation: {
            duration: animationDuration
        }
    };
}

function updateLastUpdated(timestamp) {
    const date = timestamp ? new Date(timestamp) : new Date();
    document.getElementById('lastUpdated').textContent = 
        `Ultimo aggiornamento: ${date.toLocaleTimeString('it-IT')}`;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    
    document.querySelector('.dashboard-container').prepend(errorDiv);
    
    // Rimuovi dopo 5 secondi
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function updateRecentAccess(accessi) {
    console.log('Aggiornamento accessi recenti:', accessi);
    const tableBody = document.querySelector('#recentAccessTable tbody');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    if (!accessi.length) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="no-data">Nessun accesso recente.</td>
            </tr>
        `;
        return;
    }

    accessi.forEach(accesso => {
        const row = document.createElement('tr');

        // Utente
        const utenteCell = document.createElement('td');
        utenteCell.textContent = accesso.Username;

        // Stato
        const statoCell = document.createElement('td');
        const statusBadge = document.createElement('span');
        statusBadge.className = `status-badge ${accesso.Status === 'corretto' ? 'status-success' : 'status-failed'}`;
        statusBadge.textContent = accesso.Status === 'corretto' ? 'Riuscito' : 'Fallito';
        statoCell.appendChild(statusBadge);

        // Data
        const dataCell = document.createElement('td');
        const date = new Date(accesso.Created_At);
        const time = date.toLocaleTimeString('it-IT');
        const day = date.toLocaleDateString('it-IT');
        dataCell.textContent = `${time} ${day}`;

        // Location
        const locationCell = document.createElement('td');
        locationCell.textContent = accesso.Location_Name || '—';

        row.appendChild(utenteCell);
        row.appendChild(statoCell);
        row.appendChild(locationCell);
        row.appendChild(dataCell);
        
        tableBody.appendChild(row);
    });
}