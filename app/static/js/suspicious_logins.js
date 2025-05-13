document.addEventListener('DOMContentLoaded', () => {
    const ROWS_PER_PAGE = 10;
    
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Initialize pagination for each table
    initPagination('authorized', ROWS_PER_PAGE);
    initPagination('denied', ROWS_PER_PAGE);
    
    function initPagination(tableType, rowsPerPage) {
        const table = document.getElementById(`${tableType}Table`);
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const pagination = document.getElementById(`${tableType}Pagination`);
        const prevButton = document.getElementById(`prev${tableType.charAt(0).toUpperCase() + tableType.slice(1)}Page`);
        const nextButton = document.getElementById(`next${tableType.charAt(0).toUpperCase() + tableType.slice(1)}Page`);
        const pageIndicator = pagination.querySelector('.page-indicator');
        
        let currentPage = 1;
        const totalPages = Math.max(1, Math.ceil(rows.length / rowsPerPage));
        
        function updatePagination() {
            // Show/hide rows
            rows.forEach((row, index) => {
                const shouldShow = index >= (currentPage - 1) * rowsPerPage && 
                                 index < currentPage * rowsPerPage;
                row.style.display = shouldShow ? '' : 'none';
            });
            
            // Update button states
            prevButton.disabled = currentPage === 1;
            nextButton.disabled = currentPage === totalPages;
            
            // Update page indicator
            pageIndicator.textContent = `Pagina ${currentPage} di ${totalPages}`;
            
            // Scroll to top for better UX
            if (table.offsetParent) {
                table.offsetParent.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
        
        // Event handlers
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
        
        // Initialization
        updatePagination();
    }
});