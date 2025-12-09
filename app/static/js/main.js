// Main JavaScript for DevFolio
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    initializeBootstrapComponents();
    
    // Setup form validations
    setupFormValidations();
    
    // Setup file upload previews
    setupFileUploadPreviews();
    
    // Setup analytics charts if present
    setupCharts();
    
    // Dark mode toggle
    setupDarkMode();
});

function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(toastEl => new bootstrap.Toast(toastEl));
}

function setupFormValidations() {
    // Real-time validation
    document.querySelectorAll('.needs-validation').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Character counters
    document.querySelectorAll('textarea[data-maxlength]').forEach(textarea => {
        const maxLength = textarea.dataset.maxlength;
        const counterId = textarea.dataset.counter;
        
        if (counterId && document.getElementById(counterId)) {
            const counter = document.getElementById(counterId);
            
            const updateCounter = () => {
                const length = textarea.value.length;
                counter.textContent = `${length}/${maxLength}`;
                
                counter.classList.toggle('text-warning', length > maxLength * 0.9);
                counter.classList.toggle('text-danger', length > maxLength);
            };
            
            updateCounter();
            textarea.addEventListener('input', updateCounter);
        }
    });
}

function setupFileUploadPreviews() {
    document.querySelectorAll('input[type="file"][data-preview]').forEach(input => {
        input.addEventListener('change', function(e) {
            const file = this.files[0];
            const previewId = this.dataset.preview;
            
            if (previewId && file && file.type.startsWith('image/')) {
                const preview = document.getElementById(previewId);
                if (preview) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        if (preview.tagName === 'IMG') {
                            preview.src = e.target.result;
                        } else {
                            preview.style.backgroundImage = `url(${e.target.result})`;
                            preview.style.backgroundSize = 'cover';
                        }
                        preview.classList.remove('d-none');
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    });
}

function setupCharts() {
    // Views chart
    const viewsChart = document.getElementById('viewsChart');
    if (viewsChart && typeof Chart !== 'undefined') {
        const ctx = viewsChart.getContext('2d');
        const data = JSON.parse(viewsChart.dataset.chart || '{"labels":[],"data":[]}');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Views',
                    data: data.data,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

function setupDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    
    if (toggle) {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            html.setAttribute('data-bs-theme', 'dark');
            toggle.checked = true;
        }
        
        toggle.addEventListener('change', function() {
            if (this.checked) {
                html.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                html.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
        });
    }
}

// Utility functions
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toast = `
        <div id="${toastId}" class="toast" role="alert">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toast);
    const toastEl = document.getElementById(toastId);
    new bootstrap.Toast(toastEl, { delay: 5000 }).show();
    
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// API request helper
async function makeRequest(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    if (data) options.body = JSON.stringify(data);
    
    try {
        const response = await fetch(url, options);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const contentType = response.headers.get('content-type');
        return contentType?.includes('application/json') 
            ? await response.json() 
            : await response.text();
    } catch (error) {
        console.error('Request failed:', error);
        showToast('Request failed. Please try again.', 'danger');
        throw error;
    }
}

// Image lazy loading
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img.lazy').forEach(img => imageObserver.observe(img));
}