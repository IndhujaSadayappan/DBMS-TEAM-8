// Common JavaScript functions for the application

// Show/hide password toggle
document.addEventListener('DOMContentLoaded', function() {
    // Add password toggle functionality if password fields exist
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    passwordFields.forEach(field => {
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle';
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        toggleBtn.style.position = 'absolute';
        toggleBtn.style.right = '10px';
        toggleBtn.style.top = '50%';
        toggleBtn.style.transform = 'translateY(-50%)';
        toggleBtn.style.background = 'none';
        toggleBtn.style.border = 'none';
        toggleBtn.style.cursor = 'pointer';
        toggleBtn.style.color = '#6b7280';
        
        // Wrap password field in a relative positioned div
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);
        wrapper.appendChild(toggleBtn);
        
        // Add toggle functionality
        toggleBtn.addEventListener('click', function() {
            if (field.type === 'password') {
                field.type = 'text';
                toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                field.type = 'password';
                toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add animation to elements when they come into view
function animateOnScroll() {
    const elements = document.querySelectorAll('.glass-card, .feature-card, .stat-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    elements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(element);
    });
}

// Call animation function when DOM is loaded
document.addEventListener('DOMContentLoaded', animateOnScroll);

// Add a placeholder SVG image for the counselling illustration
document.addEventListener('DOMContentLoaded', function() {
    const heroImage = document.querySelector('.hero-image img');
    if (heroImage && heroImage.src.includes('counselling.svg')) {
        // Create a placeholder SVG
        const svgData = `
        <svg xmlns="http://www.w3.org/2000/svg" width="500" height="300" viewBox="0 0 500 300">
            <rect width="500" height="300" fill="#f0f9ff" />
            <circle cx="250" cy="120" r="50" fill="#6366f1" opacity="0.7" />
            <rect x="200" y="180" width="100" height="70" rx="10" fill="#6366f1" opacity="0.5" />
            <path d="M150,200 Q250,150 350,200" stroke="#6366f1" stroke-width="5" fill="none" />
            <text x="250" y="270" font-family="Arial" font-size="16" text-anchor="middle" fill="#1f2937">Counselling System</text>
        </svg>
        `;
        
        // Convert SVG to data URL
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml' });
        const svgUrl = URL.createObjectURL(svgBlob);
        
        // Set as image source
        heroImage.src = svgUrl;
    }
});