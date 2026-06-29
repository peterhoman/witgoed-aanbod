// ============================================
// WITGOEDAANBOD.NL - Main JS
// ============================================

// Cookie Banner
document.addEventListener('DOMContentLoaded', function() {
    const cookieBanner = document.getElementById('cookie-banner');
    const cookieAccept = document.getElementById('cookie-accept');

    // Check if user already accepted
    if (!localStorage.getItem('cookies-accepted')) {
        cookieBanner.style.display = 'flex';
    } else {
        cookieBanner.style.display = 'none';
    }

    // Accept button
    if (cookieAccept) {
        cookieAccept.addEventListener('click', function() {
            localStorage.setItem('cookies-accepted', 'true');
            cookieBanner.style.display = 'none';
        });
    }

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
