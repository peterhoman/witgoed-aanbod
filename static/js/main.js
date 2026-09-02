// ============================================
// WITGOEDAANBOD.NL - Main JS
// ============================================

// ============================================
// COOKIE-TOESTEMMING
//
// Uitgangspunt (AVG): niets dat niet strikt noodzakelijk is, mag laden vóór
// de bezoeker toestemming geeft. Wegklikken is géén toestemming, dus het
// kruisje en een klik buiten het venster tellen als weigeren.
//
// De site zelf plaatst op dit moment alleen de toestemming zelf (localStorage)
// en de taalkeuze. Analytics staat klaar achter loadAnalytics() maar wordt
// pas geladen als daar toestemming voor is. De affiliate-tracking van
// Bol.com en MediaMarkt/Tradedoubler start pas op hun eigen domein, nadat de
// bezoeker zelf op een aanbieding klikt en onze site verlaat.
// ============================================
const CONSENT_KEY = 'cookie-consent';
// Ophogen zodra de tekst of de categorieën wijzigen: bezoekers met een oude
// keuze wordt dan opnieuw om toestemming gevraagd.
const CONSENT_VERSION = 2;

function getConsent() {
    try {
        const stored = JSON.parse(localStorage.getItem(CONSENT_KEY));
        if (!stored || stored.version !== CONSENT_VERSION) return null;
        return stored;
    } catch (e) {
        return null;
    }
}

function loadAnalytics() {
    // Analytics staat nu niet aan. Zetten we het aan, dan hoort de laadcode
    // hier - en dus alleen ná toestemming.
    if (!window.GA_MEASUREMENT_ID) return;
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + window.GA_MEASUREMENT_ID;
    document.head.appendChild(script);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', window.GA_MEASUREMENT_ID, { anonymize_ip: true });
}

function applyConsent(consent) {
    if (consent && consent.analytics) {
        loadAnalytics();
    }
}

// Meteen toepassen, nog vóór DOMContentLoaded: een terugkerende bezoeker die
// eerder ja zei, hoeft niet op de rest van de pagina te wachten.
applyConsent(getConsent());

document.addEventListener('DOMContentLoaded', function() {
    const cookieBalk = document.getElementById('cookie-balk');
    const balkInstellingen = document.getElementById('cookie-balk-instellingen');
    const balkReject = document.getElementById('cookie-balk-reject');
    const balkAccept = document.getElementById('cookie-balk-accept');
    const cookieModal = document.getElementById('cookie-banner');
    const cookieAccept = document.getElementById('cookie-accept');
    const cookieReject = document.getElementById('cookie-reject');
    const cookieSave = document.getElementById('cookie-save');
    const cookieClose = document.getElementById('cookie-close');
    const cookieAnalytics = document.getElementById('cookie-analytics');
    const cookieMarketing = document.getElementById('cookie-marketing');
    const cookieSettingsLink = document.getElementById('cookie-settings-link');

    if (!cookieModal) return;

    function openModal() {
        const consent = getConsent();
        if (cookieAnalytics) cookieAnalytics.checked = !!(consent && consent.analytics);
        if (cookieMarketing) cookieMarketing.checked = !!(consent && consent.marketing);
        cookieModal.classList.remove('hidden');
    }

    function saveCookieConsent(analytics, marketing) {
        const consent = {
            version: CONSENT_VERSION,
            essential: true,
            analytics: !!analytics,
            marketing: !!marketing,
            date: new Date().toISOString()
        };
        localStorage.setItem(CONSENT_KEY, JSON.stringify(consent));
        cookieModal.classList.add('hidden');
        if (cookieBalk) cookieBalk.classList.add('hidden');
        document.body.classList.remove('cookiebalk-open');
        applyConsent(consent);
    }

    // Geen keuze gemaakt: toon de BALK onderaan, niet het venster
    // (designrapport punt 12). De pagina blijft leesbaar en bedienbaar;
    // het venster komt alleen nog op verzoek (instellingenknop).
    if (!getConsent() && cookieBalk) {
        cookieBalk.classList.remove('hidden');
        // Zolang de balk er staat, gaat de babbelbotknop weg. Die knop staat
        // vast rechtsonder op laag 9000 en de balk op laag 2000, dus hij lag
        // precies over "Alles accepteren" heen -- op een telefoon over 96%
        // van die knop, op een computer over de hele knop. Wie accepteren
        // wilde, opende de chatbot, en de balk bleef staan. Eerst kiezen,
        // dan pas de bot.
        document.body.classList.add('cookiebalk-open');
    }

    if (balkReject) {
        balkReject.addEventListener('click', function() {
            saveCookieConsent(false, false);
        });
    }

    if (balkAccept) {
        balkAccept.addEventListener('click', function() {
            saveCookieConsent(true, true);
        });
    }

    if (balkInstellingen) {
        balkInstellingen.addEventListener('click', function() {
            openModal();
        });
    }

    if (cookieAccept) {
        cookieAccept.addEventListener('click', function() {
            saveCookieConsent(true, true);
        });
    }

    if (cookieSave) {
        cookieSave.addEventListener('click', function() {
            saveCookieConsent(cookieAnalytics && cookieAnalytics.checked,
                              cookieMarketing && cookieMarketing.checked);
        });
    }

    if (cookieReject) {
        cookieReject.addEventListener('click', function() {
            saveCookieConsent(false, false);
        });
    }

    // Het venster wordt alleen nog vrijwillig geopend; het wegklikken
    // (kruisje of klik ernaast) is dus geen keuze maar "laat maar even".
    // Zonder keuze blijft de balk gewoon staan. Wegklikken mag nooit als
    // "ja" gelden, en telt nu ook niet meer stilzwijgend als "nee".
    if (cookieClose) {
        cookieClose.addEventListener('click', function() {
            cookieModal.classList.add('hidden');
        });
    }

    cookieModal.addEventListener('click', function(e) {
        if (e.target === cookieModal) {
            cookieModal.classList.add('hidden');
        }
    });

    // Toestemming later wijzigen of intrekken (link in de voettekst).
    if (cookieSettingsLink) {
        cookieSettingsLink.addEventListener('click', function(e) {
            e.preventDefault();
            openModal();
        });
    }
});

// De rest staat bewust in een eigen blok: de cookiecode hierboven stopt als
// er geen banner op de pagina staat, en dat mag lazy loading en de
// prijsfilters niet meeslepen.
document.addEventListener('DOMContentLoaded', function() {
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
            const checked = ids.includes(parseInt(checkbox.dataset.productId, 10));
            checkbox.checked = checked;
            const label = checkbox.closest('.compare-label');
            if (label) label.classList.toggle('is-checked', checked);
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

// ============================================
// WISHLIST (verlanglijst, localStorage, geen account)
// ============================================
(function() {
    const STORAGE_KEY = 'wishlist-products';
    const HEART_EMPTY = '♡';
    const HEART_FILLED = '♥';

    function getWishlist() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch (e) {
            return [];
        }
    }

    function saveWishlist(list) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
        syncButtons();
        renderNavCount();
    }

    function toggleWishlist(id, title) {
        let list = getWishlist();
        const existingIndex = list.findIndex(item => item.id === id);
        if (existingIndex > -1) {
            list.splice(existingIndex, 1);
        } else {
            list.push({ id: id, title: title });
        }
        saveWishlist(list);
    }

    function syncButtons() {
        const ids = getWishlist().map(item => item.id);
        document.querySelectorAll('.wishlist-toggle').forEach(function(btn) {
            const active = ids.includes(parseInt(btn.dataset.productId, 10));
            btn.classList.toggle('is-active', active);
            const glyph = btn.querySelector('span[aria-hidden]') || btn;
            // Kaartjes-hartje heeft geen los <span>: hele knop is de glyph.
            if (btn.classList.contains('wishlist-toggle-large')) {
                glyph.textContent = active ? HEART_FILLED : HEART_EMPTY;
                const label = btn.querySelector('.wishlist-toggle-label');
                if (label) label.textContent = active ? wishlistLabels.remove : wishlistLabels.add;
            } else {
                btn.innerHTML = active ? HEART_FILLED : HEART_EMPTY;
            }
        });
    }

    function renderNavCount() {
        const count = getWishlist().length;
        const link = document.getElementById('wishlist-nav-link');
        const counter = document.getElementById('wishlist-nav-count');
        if (!link || !counter) return;
        counter.textContent = count;
        link.classList.toggle('has-items', count > 0);
        if (count > 0) {
            link.href = '/verlanglijst?ids=' + getWishlist().map(i => i.id).join(',');
        }
    }

    // Labels komen uit de pagina zelf (data-attributen op <body>) zodat de
    // NL/EN-vertaling uit translations.py ook hier klopt, zonder een aparte
    // JS-vertaaltabel te hoeven onderhouden.
    const wishlistLabels = {
        add: document.body.dataset.wishlistAdd || 'Toevoegen aan verlanglijst',
        remove: document.body.dataset.wishlistRemove || 'In verlanglijst',
    };

    document.addEventListener('DOMContentLoaded', function() {
        document.body.addEventListener('click', function(e) {
            const btn = e.target.closest('.wishlist-toggle');
            if (!btn) return;
            e.preventDefault();
            const id = parseInt(btn.dataset.productId, 10);
            const title = btn.dataset.productTitle || '';
            toggleWishlist(id, title);
        });

        syncButtons();
        renderNavCount();
    });
})();

// ============================================
// CATEGORIES CAROUSEL (homepage)
// ============================================
document.querySelectorAll('.carousel').forEach(function(carousel) {
    const track = carousel.querySelector('.carousel-track');
    const left = carousel.querySelector('.carousel-arrow-left');
    const right = carousel.querySelector('.carousel-arrow-right');
    if (!track || !left || !right) return;

    const scrollAmount = () => track.clientWidth * 0.8;
    left.addEventListener('click', () => track.scrollBy({ left: -scrollAmount(), behavior: 'smooth' }));
    right.addEventListener('click', () => track.scrollBy({ left: scrollAmount(), behavior: 'smooth' }));
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

// ============================================
// FILTER: "MEER (N)" IN DE ZIJBALK
// ============================================
// Lange optielijsten (merken, kleuren) tonen de eerste zes; de rest zit
// achter deze knop. Voorheen stonden ze allemaal in een blok met een vaste
// hoogte en een eigen scrollbalk, wat scrollen boven de zijbalk kaapte.
document.querySelectorAll('.filter-meer').forEach(function (knop) {
    knop.addEventListener('click', function () {
        const lijst = knop.previousElementSibling;
        if (!lijst || !lijst.classList.contains('filter-opties')) return;
        lijst.classList.add('toont-alles');
        knop.remove();
    });
});

// ============================================
// VIDEO PAS NA EEN TIK
// ============================================
// Het YouTube-iframe haalt een halve megabyte aan eigen scripts op, ook
// als niemand op afspelen drukt. De pagina toont daarom alleen het
// voorbeeldplaatje (video_facade in _macros.html); het iframe wordt hier
// pas gebouwd na de eerste tik, met autoplay zodat die ene tik ook
// meteen afspeelt. Geen 'web-share' in allow: dat kende de browser niet
// en was de enige melding in de console.
document.querySelectorAll('.video-facade').forEach(function (knop) {
    knop.addEventListener('click', function () {
        const iframe = document.createElement('iframe');
        iframe.src = knop.dataset.embed;
        iframe.title = knop.dataset.titel || '';
        iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
        iframe.setAttribute('allowfullscreen', '');
        iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
        knop.replaceWith(iframe);
    });
});

// ============================================
// FILTER: ZOEKEN BINNEN EEN GROTE OPTIELIJST
// ============================================
// Groepen met meer dan 25 opties tonen de twintig grootste; de rest bereik
// je door te typen. Leeg veld = terug naar het normale gedrag, dus we halen
// de inline stijl weg en laten de CSS het weer overnemen.
document.querySelectorAll('.filter-zoek').forEach(function (veld) {
    const lijst = veld.nextElementSibling;
    if (!lijst || !lijst.classList.contains('filter-opties')) return;
    const labels = Array.prototype.slice.call(lijst.querySelectorAll('.checkbox-label'));
    veld.addEventListener('input', function () {
        const zoek = veld.value.trim().toLowerCase();
        labels.forEach(function (label) {
            if (!zoek) {
                label.style.display = '';
                return;
            }
            label.style.display = label.textContent.toLowerCase().indexOf(zoek) !== -1 ? 'flex' : 'none';
        });
    });
});
