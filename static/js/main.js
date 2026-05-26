// Main JavaScript for Cattle Disease Prediction System

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const offsetTop = target.offsetTop - 80; // Account for fixed navbar
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Navbar background change on scroll
    const navbar = document.querySelector('.navbar');
    if (navbar && navbar.classList.contains('fixed-top')) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
            } else {
                navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
            }
        });
    }

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe service cards and step cards
    document.querySelectorAll('.service-card, .step-card, .audience-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease-out';
        observer.observe(card);
    });
    
    // Get user location for GPS coordinates
    if (navigator.geolocation) {
        const locationButtons = document.querySelectorAll('.get-location');
        locationButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const latInput = document.getElementById('id_latitude');
                        const lngInput = document.getElementById('id_longitude');
                        if (latInput && lngInput) {
                            latInput.value = position.coords.latitude.toFixed(6);
                            lngInput.value = position.coords.longitude.toFixed(6);
                            alert('Location captured successfully!');
                        }
                    },
                    function(error) {
                        alert('Unable to get your location. Please enter manually.');
                    }
                );
            });
        });
    }
});
