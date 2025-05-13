document.addEventListener('DOMContentLoaded', () => {
    const ROWS_PER_PAGE = 10;
    const table = document.getElementById('historyTable');
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const pagination = document.getElementById('historyPagination');
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');
    const pageIndicator = pagination.querySelector('.page-indicator');
    
    let currentPage = 1;
    const totalPages = Math.max(1, Math.ceil(rows.length / ROWS_PER_PAGE));

    function updatePagination() {
        rows.forEach((row, index) => {
            const shouldShow = index >= (currentPage - 1) * ROWS_PER_PAGE && 
                             index < currentPage * ROWS_PER_PAGE;
            row.style.display = shouldShow ? '' : 'none';
        });

        prevButton.disabled = currentPage === 1;
        nextButton.disabled = currentPage === totalPages;
        
        pageIndicator.textContent = `Pagina ${currentPage} di ${totalPages}`;
        
        if (table.offsetParent) {
            table.offsetParent.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            updatePagination();
        }
    });

    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            updatePagination();
        }
    });

    updatePagination();
});