// ============================================
// WITGOEDAANBOD.NL - Main JS
// ============================================

// Cookie Consent Modal
document.addEventListener('DOMContentLoaded', function() {
    const cookieModal = document.getElementById('cookie-banner');
    const cookieAccept = document.getElementById('cookie-accept');
    const cookieReject = document.getElementById('cookie-reject');
    const cookieClose = document.getElementById('cookie-close');
    const cookieAnalytics = document.getElementById('cookie-analytics');
    const cookieMarketing = document.getElementById('cookie-marketing');

    function showCookieModal() {
        if (!localStorage.getItem('cookie-consent')) {
            cookieModal.classList.remove('hidden');
        }
    }

    function saveCookieConsent(analytics = false, marketing = false) {
        const consent = {
            essential: true,
            analytics: analytics,
            marketing: marketing,
            date: new Date().toISOString()
        };
        localStorage.setItem('cookie-consent', JSON.stringify(consent));
        cookieModal.classList.add('hidden');

        if (analytics) {
            loadAnalytics();
        }
    }

    function loadAnalytics() {
        // Load Google Analytics or other tracking
        console.log('[Analytics] Tracking enabled');
    }

    // Show modal on first visit
    showCookieModal();

    // Accept all
    if (cookieAccept) {
        cookieAccept.addEventListener('click', function() {
            saveCookieConsent(true, true);
        });
    }

    // Reject (essential only)
    if (cookieReject) {
        cookieReject.addEventListener('click', function() {
            saveCookieConsent(false, false);
        });
    }

    // Close button
    if (cookieClose) {
        cookieClose.addEventListener('click', function() {
            cookieModal.classList.add('hidden');
        });
    }

    // Close on outside click
    cookieModal.addEventListener('click', function(e) {
        if (e.target === cookieModal) {
            cookieModal.classList.add('hidden');
        }
    });

    // Lazy loading images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Price filter listeners (if on category/search page)
    const minPriceInput = document.getElementById('min_price');
    const maxPriceInput = document.getElementById('max_price');
    const minPriceLabel = document.getElementById('min-price-label');
    const maxPriceLabel = document.getElementById('max-price-label');

    if (minPriceInput && minPriceLabel) {
        minPriceInput.addEventListener('input', function() {
            minPriceLabel.textContent = this.value;
        });
    }

    if (maxPriceInput && maxPriceLabel) {
        maxPriceInput.addEventListener('input', function() {
            maxPriceLabel.textContent = this.value;
        });
    }
});

// Smooth scroll behavior (fallback for older browsers)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
