document.addEventListener('DOMContentLoaded', function () {

    // === GESTIONE TEMA CHIARO/SCURO ===
    function isDarkTheme() {
        const html = document.documentElement;
        return html.classList.contains('dark-theme') ||
            document.getElementById('theme-style')?.getAttribute('href')?.includes('dark');
    }

    function getTextColor() {
        return isDarkTheme() ? '#ffffff' : '#000000';
    }

    function getBgColor() {
        return isDarkTheme() ? '#1e1e1e' : '#ffffff';
    }

    function getBorderColor() {
        return isDarkTheme() ? '#333333' : '#cccccc';
    }

    // === GRAFICO RUOLI ===
    const ctx = document.getElementById('usersChart').getContext('2d');
    const userChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Amministratori', 'Utenti', 'Ospiti'],
            datasets: [{
                data: [roleDistribution.admin || 0, roleDistribution.user || 0, roleDistribution.guest || 0],
                backgroundColor: ['#3a86ff', '#06d6a0', '#ffbe0b'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: getTextColor(),
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            const label = ctx.label || '';
                            const value = ctx.raw || 0;
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    },
                    titleColor: getTextColor(),
                    bodyColor: getTextColor(),
                    backgroundColor: getBgColor(),
                    borderColor: getBorderColor(),
                    borderWidth: 1
                }
            },
            cutout: '65%'
        }
    });

    // === GRAFICO ACCESSI OGGI PER UTENTE (DINAMICO) ===
    let accessiChart;

    fetch('/api/stats/aggregate')
        .then(response => response.json())
        .then(data => {
            const accessiOggi = data.accessi_oggi_per_utente;

            const ctx2 = document.getElementById('accessiOggiChart').getContext('2d');
            accessiChart = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: accessiOggi.map(item => item.username),
                    datasets: [{
                        data: accessiOggi.map(item => item.count),
                        backgroundColor: [
                            '#3a86ff', '#ff006e', '#8338ec', '#06d6a0', '#ffbe0b',
                            '#fb5607', '#ff006e', '#8338ec', '#3a86ff', '#06d6a0'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: getTextColor(),
                                font: { size: 12 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (ctx) {
                                    const label = ctx.label || '';
                                    const value = ctx.raw || 0;
                                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} accessi (${percentage}%)`;
                                }
                            },
                            titleColor: getTextColor(),
                            bodyColor: getTextColor(),
                            backgroundColor: getBgColor(),
                            borderColor: getBorderColor(),
                            borderWidth: 1
                        }
                    },
                    cutout: '65%'
                }
            });

            updateChartColors();
        })
        .catch(error => {
            console.error("Errore durante il caricamento accessi oggi:", error);
        });

    // === AGGIORNA COLORI GRAFICI ===
    function updateChartColors() {
        const textColor = getTextColor();
        const bgColor = getBgColor();
        const borderColor = getBorderColor();

        [userChart, accessiChart].forEach(chart => {
            if (!chart) return;
            chart.options.plugins.legend.labels.color = textColor;
            chart.options.plugins.tooltip.titleColor = textColor;
            chart.options.plugins.tooltip.bodyColor = textColor;
            chart.options.plugins.tooltip.backgroundColor = bgColor;
            chart.options.plugins.tooltip.borderColor = borderColor;
            chart.update();
        });
    }

    const themeObserver = new MutationObserver(updateChartColors);
    themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class', 'style']
    });

    updateChartColors();

    // === DELETE USER MODAL ===
    document.querySelectorAll('.delete-user').forEach(btn => {
        btn.addEventListener('click', () => {
            const userId = btn.getAttribute('data-userid');
            const userName = btn.closest('.user-item').querySelector('.user-name').textContent;

            document.getElementById('deleteUserId').value = userId;
            document.getElementById('deleteUserMessage').textContent =
                `Sei sicuro di voler eliminare l'utente: ${userName}?`;
            document.getElementById('deleteUserModal').style.display = 'flex';
        });
    });

    document.getElementById('confirmDeleteUser').addEventListener('click', function () {
        const id = document.getElementById('deleteUserId').value;
        fetch(`/api/users/${id}`, { method: 'DELETE' })
            .then(res => res.ok ? location.reload() : alert('Errore nella cancellazione'));
    });

    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
        });
    });

    // === EDIT USER MODAL ===
    document.querySelectorAll('.edit-user').forEach(btn => {
        btn.addEventListener('click', () => {
            const userId = btn.getAttribute('data-userid');
            const userCard = btn.closest('.user-item');
            const username = userCard.querySelector('.user-name').childNodes[0].nodeValue.trim();
            const role = userCard.querySelector('.user-role').innerText.toLowerCase();
            const roleSelect = document.getElementById('editRole');

            // Verifica e imposta solo se il valore è valido
            const validRoles = ['admin', 'user', 'guest'];
            if (validRoles.includes(role)) {
                roleSelect.value = role;
            } else {
                roleSelect.value = 'user'; // valore di fallback predefinito
            }

            document.getElementById('editUserId').value = userId;
            document.getElementById('editUsername').value = username;
            document.getElementById('editRole').value = roleSelect.value;
            document.getElementById('editUserModal').style.display = 'flex';
        });
    });

    document.getElementById('saveUserChanges').addEventListener('click', function () {
        const id = document.getElementById('editUserId').value;
        const newUsername = document.getElementById('editUsername').value;
        const newRole = document.getElementById('editRole').value;
        const generatePassword = document.getElementById('editPassword').checked

        fetch(`/api/users/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: newUsername,
                role: newRole,
                password: generatePassword  // booleano vero/falso
            })
        }).then(res => res.ok ? location.reload() : alert('Errore nel salvataggio'));
    });

    // === PAGINAZIONE AVANTI/INDIETRO ===
    const usersPerPage = 3;
    const userList = document.querySelectorAll('.user-item');
    const container = document.querySelector('.user-list');
    const pageNav = document.createElement('div');
    pageNav.className = 'pagination-nav';
    container.parentElement.appendChild(pageNav);

    let currentPage = 1;
    const totalPages = Math.ceil(userList.length / usersPerPage);

    function renderPage(page) {
        userList.forEach((el, i) => {
            el.style.display = (i >= (page - 1) * usersPerPage && i < page * usersPerPage) ? 'flex' : 'none';
        });

        pageNav.innerHTML = '';

        const prev = document.createElement('button');
        prev.textContent = '◀';
        prev.disabled = (page === 1);
        prev.className = 'pagination-btn';
        prev.onclick = () => renderPage(page - 1);
        pageNav.appendChild(prev);

        const next = document.createElement('button');
        next.textContent = '▶';
        next.disabled = (page === totalPages);
        next.className = 'pagination-btn';
        next.onclick = () => renderPage(page + 1);
        pageNav.appendChild(next);
    }

    if (userList.length > usersPerPage) {
        renderPage(currentPage);
    }
});
