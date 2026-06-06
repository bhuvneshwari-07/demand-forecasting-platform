/* ==========================================================================
   AI Demand Forecasting & Inventory Intelligence Platform - Theme Toggle JS
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
    // Check local storage for theme setting
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
            
            // Optionally update database configuration via simple async fetch if authenticated
            fetch('/settings/toggle-theme/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ theme: newTheme })
            }).catch(err => console.log('Session theme sync skipped or unavailable'));
        });
    }
});
function applyTheme(theme) {
    if (theme === 'light') {
        document.body.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
        updateToggleIcon(true);
    } else {
        document.body.classList.remove('light-theme');
        localStorage.setItem('theme', 'dark');
        updateToggleIcon(false);
    }
}
function updateToggleIcon(isLight) {
    const icon = document.querySelector('#theme-toggle-btn i');
    const label = document.querySelector('#theme-toggle-text');
    if (icon) {
        if (isLight) {
            icon.className = 'fas fa-moon';
        } else {
            icon.className = 'fas fa-sun';
        }
    }
    if (label) {
        label.textContent = isLight ? 'Switch to Dark Mode' : 'Switch to Light Mode';
    }
}
// Utility to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
