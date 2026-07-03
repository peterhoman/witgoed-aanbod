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

// ============================================
// PRODUCT COMPARISON (max 3 producten, localStorage)
// ============================================
(function() {
    const STORAGE_KEY = 'compare-products';
    const MAX_COMPARE = 3;

    function getCompareList() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch (e) {
            return [];
        }
    }

    function saveCompareList(list) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
        renderCompareBar();
        syncCheckboxes();
    }

    function toggleCompare(id, title) {
        let list = getCompareList();
        const existingIndex = list.findIndex(item => item.id === id);

        if (existingIndex > -1) {
            list.splice(existingIndex, 1);
        } else {
            if (list.length >= MAX_COMPARE) {
                alert('Je kunt maximaal ' + MAX_COMPARE + ' producten tegelijk vergelijken. Verwijder eerst een product uit je vergelijking.');
                return;
            }
            list.push({ id: id, title: title });
        }
        saveCompareList(list);
    }

    function syncCheckboxes() {
        const list = getCompareList();
        const ids = list.map(item => item.id);
        document.querySelectorAll('.compare-checkbox').forEach(function(checkbox) {
            checkbox.checked = ids.includes(parseInt(checkbox.dataset.productId, 10));
        });
    }

    function renderCompareBar() {
        const list = getCompareList();
        let bar = document.getElementById('compare-bar');

        if (list.length === 0) {
            if (bar) bar.remove();
            return;
        }

        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'compare-bar';
            bar.className = 'compare-bar';
            document.body.appendChild(bar);
        }

        const ids = list.map(item => item.id).join(',');
        bar.innerHTML =
            '<div class="compare-bar-header">' +
                '<span class="compare-bar-count">Vergelijk (' + list.length + '/' + MAX_COMPARE + ')</span>' +
                '<button type="button" class="compare-bar-clear" title="Wis vergelijking">&times;</button>' +
            '</div>' +
            '<span class="compare-bar-items">' + list.map(item => item.title.substring(0, 30)).join(' vs. ') + '</span>' +
            '<a href="/vergelijk?ids=' + ids + '" class="btn-buy compare-bar-cta">Vergelijk nu →</a>';

        bar.querySelector('.compare-bar-clear').addEventListener('click', function() {
            saveCompareList([]);
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.compare-checkbox').forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                const id = parseInt(this.dataset.productId, 10);
                const title = this.dataset.productTitle || '';
                toggleCompare(id, title);
            });
        });

        if (window.location.pathname === '/vergelijk') {
            // Vergelijking bekeken = klaar. Keuze legen zodat je niet later,
            // op een heel andere pagina, tegen "max 3" aanloopt met
            // producten die je niet meer kunt terugvinden of uitvinken.
            saveCompareList([]);
        } else {
            syncCheckboxes();
            renderCompareBar();
        }
    });
})();

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
