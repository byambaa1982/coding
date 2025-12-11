// Main JavaScript file
console.log('Tutorial E-Commerce Platform loaded');

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert, [class*="bg-green"], [class*="bg-red"], [class*="bg-yellow"], [class*="bg-blue"]');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
