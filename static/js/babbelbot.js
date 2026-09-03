/* Babbelbot — advies-chatbot van WitgoedAanbod.nl.
 *
 * Zelfstandig, herbruikbaar bestand: injecteert zijn eigen knop, venster en
 * stijlen. Inladen = één regel op elke pagina:
 *   <script src="/static/js/babbelbot.js" defer></script>
 * Praat met POST /api/chat-advies (routes/chat.py); alle productdata in de
 * antwoorden komt server-side uit de eigen database.
 */
(function () {
    'use strict';

    var VOORBEELDVRAAG = 'Ik zoek een wasmachine die ook kan drogen';

    var css = [
        '#babbelbot-knop{position:fixed;bottom:20px;right:20px;z-index:9000;',
        ' background:var(--primary,#0090DA);color:#fff;border:none;border-radius:24px;',
        ' padding:12px 20px;font-size:15px;font-weight:600;cursor:pointer;',
        ' box-shadow:0 2px 10px rgba(0,0,0,.2);font-family:inherit;}',
        '#babbelbot-knop:hover{background:var(--primary-dark,#0072AD);}',
        /* Geopend venster verticaal gecentreerd (feedback Peter): zo hangt
           het typvak rond het midden van het scherm i.p.v. in de onderhoek.
           De knop zelf blijft op de vertrouwde chat-plek rechtsonder. */
        '#babbelbot-venster{position:fixed;top:50%;right:20px;transform:translateY(-50%);z-index:9001;',
        ' width:min(440px,calc(100vw - 24px));height:min(660px,calc(100vh - 32px));',
        ' background:#fff;border:1px solid var(--border,#E0E0E0);border-radius:12px;',
        ' box-shadow:0 4px 24px rgba(0,0,0,.18);display:none;flex-direction:column;overflow:hidden;}',
        '#babbelbot-venster.open{display:flex;}',
        '#babbelbot-kop{background:var(--primary,#0090DA);color:#fff;padding:14px 16px;',
        ' display:flex;justify-content:space-between;align-items:center;}',
        '#babbelbot-kop strong{font-size:16px;}',
        '#babbelbot-kop small{display:block;font-weight:400;font-size:11.5px;opacity:.9;margin-top:2px;}',
        '#babbelbot-sluit{background:none;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1;padding:4px;}',
        '#babbelbot-berichten{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:var(--light,#F8F9FA);}',
        '.babbelbot-bericht{max-width:88%;padding:9px 13px;border-radius:10px;font-size:14px;line-height:1.5;}',
        '.babbelbot-bezoeker{align-self:flex-end;background:var(--secondary-light,#E3F2FD);color:var(--dark,#212529);}',
        '.babbelbot-bot{align-self:flex-start;background:#fff;border:1px solid var(--border,#E0E0E0);color:var(--dark,#212529);}',
        '.babbelbot-kaart{background:#fff;border:1px solid var(--border,#E0E0E0);border-radius:10px;padding:11px 13px;align-self:stretch;}',
        '.babbelbot-kaart strong{font-size:13.5px;display:block;margin-bottom:2px;}',
        '.babbelbot-kaart .babbelbot-prijs{font-size:14px;font-weight:700;color:var(--dark,#212529);}',
        '.babbelbot-kaart .babbelbot-winkels{font-size:11.5px;color:var(--gray,#6C757D);margin-left:6px;}',
        '.babbelbot-kaart p{font-size:12.5px;color:var(--gray,#6C757D);margin:6px 0;line-height:1.45;}',
        '.babbelbot-kaart a{display:inline-block;background:var(--primary,#0090DA);color:#fff;text-decoration:none;',
        ' font-size:12.5px;font-weight:600;padding:7px 13px;border-radius:6px;}',
        '.babbelbot-kaart a:hover{background:var(--primary-dark,#0072AD);}',
        '#babbelbot-voorbeeld{margin:0 14px;padding:7px 12px;font-size:12.5px;border:1px dashed var(--border,#E0E0E0);',
        ' border-radius:8px;background:#fff;color:var(--gray,#6C757D);cursor:pointer;text-align:left;font-family:inherit;}',
        '#babbelbot-voorbeeld:hover{border-color:var(--primary,#0090DA);color:var(--primary,#0090DA);}',
        '#babbelbot-invoer{display:flex;gap:8px;padding:12px 14px;background:#fff;border-top:1px solid var(--border,#E0E0E0);align-items:flex-end;}',
        '#babbelbot-invoer textarea{flex:1;border:1px solid var(--border,#E0E0E0);border-radius:8px;padding:10px 12px;',
        ' font-size:15px;font-family:inherit;line-height:1.45;resize:none;overflow-y:hidden;max-height:104px;}',
        '#babbelbot-invoer button{background:var(--primary,#0090DA);border:none;color:#fff;font-weight:600;',
        ' padding:9px 16px;border-radius:8px;cursor:pointer;font-size:14px;font-family:inherit;}',
        '#babbelbot-invoer button:disabled{opacity:.5;cursor:default;}',
        '#babbelbot-disclaimer{font-size:10.5px;color:var(--gray,#6C757D);padding:0 14px 10px;background:#fff;}',
    ].join('');

    function maakElement(html) {
        var d = document.createElement('div');
        d.innerHTML = html;
        return d.firstElementChild;
    }

    function init() {
        var stijl = document.createElement('style');
        stijl.textContent = css;
        document.head.appendChild(stijl);

        /* AI-transparantie (EU AI-verordening, geldt vanaf 2 augustus 2026):
           wie met een AI-systeem praat moet dat verteld worden. Vandaar
           "AI" in de naam, de ondertitel in de kop en de zin in het
           welkomstbericht — drie plekken, zodat het ook duidelijk is voor
           wie de kop overslaat of het venster al open had staan. */
        // Het opschrift zit in een eigen span, zodat het op een telefoon kan
        // wijken en er een ronde knop van 52 pixels overblijft (main.css).
        // De volledige naam blijft in aria-label staan, dus een schermlezer
        // hoort hem nog steeds.
        var knop = maakElement('<button id="babbelbot-knop" type="button" aria-label="Vraag de AI-Babbelbot">' +
            '<span aria-hidden="true">&#128172;</span>' +
            '<span class="babbelbot-label"> Vraag de AI-Babbelbot</span></button>');
        var venster = maakElement(
            '<div id="babbelbot-venster" role="dialog" aria-label="AI-Babbelbot productadvies">' +
            '<div id="babbelbot-kop"><div><strong>AI-Babbelbot</strong>' +
            '<small>Automatisch productadvies (AI) &mdash; je chat niet met een medewerker</small></div>' +
            '<button id="babbelbot-sluit" type="button" aria-label="Sluiten">&times;</button></div>' +
            '<div id="babbelbot-berichten"></div>' +
            '<button id="babbelbot-voorbeeld" type="button">Bijvoorbeeld: &ldquo;' + VOORBEELDVRAAG + '&rdquo;</button>' +
            '<form id="babbelbot-invoer"><textarea rows="1" maxlength="500" ' +
            'placeholder="Stel je vraag aan de AI-Babbelbot" aria-label="Je vraag"></textarea>' +
            '<button type="submit">Vraag</button></form>' +
            '<div id="babbelbot-disclaimer">De AI-Babbelbot is een computerprogramma en vergelijkt alleen producten ' +
            'op WitgoedAanbod.nl &mdash; wij zijn een onafhankelijke prijsvergelijker, geen winkel. AI-antwoorden ' +
            'kunnen fouten bevatten; controleer prijs en voorraad altijd bij de winkel zelf.</div>' +
            '</div>');
        document.body.appendChild(knop);
        document.body.appendChild(venster);

        var berichten = venster.querySelector('#babbelbot-berichten');
        var formulier = venster.querySelector('#babbelbot-invoer');
        var invoer = formulier.querySelector('textarea');
        var verstuurKnop = formulier.querySelector('button');
        var voorbeeld = venster.querySelector('#babbelbot-voorbeeld');

        // Tekstvak groeit mee met wat je typt (tot ~4 regels), zodat je
        // altijd ziet wat er staat; Enter verstuurt, Shift+Enter = nieuwe regel.
        function groei() {
            invoer.style.height = 'auto';
            invoer.style.height = Math.min(invoer.scrollHeight, 104) + 'px';
        }
        invoer.addEventListener('input', groei);
        invoer.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                formulier.dispatchEvent(new Event('submit', { cancelable: true }));
            }
        });

        function voegBericht(node) {
            berichten.appendChild(node);
            berichten.scrollTop = berichten.scrollHeight;
        }

        function botTekst(tekst) {
            var b = maakElement('<div class="babbelbot-bericht babbelbot-bot"></div>');
            b.textContent = tekst;
            voegBericht(b);
            return b;
        }

        function toonProducten(data) {
            if (data.toelichting) { botTekst(data.toelichting); }
            (data.producten || []).forEach(function (p) {
                var kaart = maakElement('<div class="babbelbot-kaart"></div>');
                var titel = document.createElement('strong');
                titel.textContent = p.naam;
                var prijs = maakElement('<span class="babbelbot-prijs"></span>');
                prijs.textContent = '€ ' + p.prijs;
                var winkels = maakElement('<span class="babbelbot-winkels"></span>');
                if (p.winkels > 1) { winkels.textContent = 'bij ' + p.winkels + ' winkels'; }
                var reden = document.createElement('p');
                reden.textContent = p.reden;
                var link = maakElement('<a></a>');
                link.href = p.url;
                link.textContent = 'Bekijk alle prijzen →';
                kaart.appendChild(titel);
                kaart.appendChild(prijs);
                kaart.appendChild(winkels);
                kaart.appendChild(reden);
                kaart.appendChild(link);
                voegBericht(kaart);
            });
        }

        function verstuur(vraag) {
            var mijn = maakElement('<div class="babbelbot-bericht babbelbot-bezoeker"></div>');
            mijn.textContent = vraag;
            voegBericht(mijn);
            invoer.value = '';
            groei();
            verstuurKnop.disabled = true;
            var bezig = botTekst('Even zoeken…');

            fetch('/api/chat-advies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vraag: vraag })
            }).then(function (r) { return r.json(); })
              .then(function (data) {
                bezig.remove();
                if (data.type === 'advies') { toonProducten(data); }
                else { botTekst(data.tekst || 'Er ging iets mis. Probeer het opnieuw.'); }
            }).catch(function () {
                bezig.remove();
                botTekst('Er ging iets mis. Probeer het zo opnieuw.');
            }).finally(function () {
                verstuurKnop.disabled = false;
                invoer.focus();
            });
        }

        knop.addEventListener('click', function () {
            venster.classList.add('open');
            knop.style.display = 'none';
            if (!berichten.children.length) {
                botTekst('Hoi! Ik ben de AI-Babbelbot, een computerhulpje — je chat hier ' +
                         'dus niet met een mens. Vertel wat je zoekt — bijvoorbeeld het ' +
                         'soort apparaat, je budget of je gezinssituatie — dan zoek ik met je mee.');
            }
            invoer.focus();
        });
        venster.querySelector('#babbelbot-sluit').addEventListener('click', function () {
            venster.classList.remove('open');
            knop.style.display = '';
        });
        voorbeeld.addEventListener('click', function () {
            invoer.value = VOORBEELDVRAAG;
            groei();
            invoer.focus();
        });
        formulier.addEventListener('submit', function (e) {
            e.preventDefault();
            var vraag = invoer.value.trim();
            if (vraag) { verstuur(vraag); }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
