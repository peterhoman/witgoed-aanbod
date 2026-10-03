"""Kaartje voor de doorklik naar een winkel.

Waarom dit bestaat (3 oktober 2026)
-----------------------------------
Tijdens Peters vakantie liep de doorklikteller op van ~10 naar 3.500 per dag
(1 okt 633, 2 okt 3.142, 3 okt 3.500 om half negen). Gemeten in de Railway-
logs: elk verzoek op /uit/aanbieding/<id> kwam van een ander IP-adres
(147 verzoeken, 147 adressen, allemaal Chinese mobiele netwerken, binnen via
het Amerikaanse Railway-knooppunt), geen van die adressen laadde ooit een
productpagina, en de verzoeken deden zich voor als browser mét de juiste
Sec-Fetch-koppen. De controles in pageviews.bron zagen ze dus als mens, en
elk verzoek werd doorgestuurd naar het affiliate-netwerk en daar als klik
geteld. Duizenden kliks zonder verkoop is precies het patroon waarop een
netwerk een account markeert.

Per IP begrenzen helpt niet (elk verzoek een ander adres) en de koppen zijn
vervalst. Wat een mens wel doet en dit botnet niet: eerst de productpagina
laden. Daarom krijgt elke winkelknop bij het renderen van de pagina een
kaartje mee: een tijdstempel plus een handtekening over aanbieding en
tijdstempel, gemaakt met de geheime sleutel van de site. De doorklikroute
stuurt alleen door met een geldig kaartje van hooguit twaalf uur oud. Zonder
kaartje gaat de bezoeker naar de productpagina (daar staat een verse knop),
niet naar het netwerk.

Geen cookie, geen IP, geen sessie: het kaartje zegt alleen "deze link komt
van een pagina die wij minder dan twaalf uur geleden hebben uitgegeven".
"""
import hashlib
import hmac
import time

GELDIG_UREN = 12


def _handtekening(sleutel, soort, nummer, tijdstempel):
    bericht = f"{soort}:{nummer}:{tijdstempel}".encode()
    return hmac.new(str(sleutel).encode(), bericht, hashlib.sha256).hexdigest()[:20]


def maak_kaartje(sleutel, soort, nummer, nu=None):
    """Kaartje voor één knop: '<tijdstempel>.<handtekening>'."""
    tijdstempel = int(nu if nu is not None else time.time())
    return f"{tijdstempel}.{_handtekening(sleutel, soort, nummer, tijdstempel)}"


def kaartje_geldig(kaartje, sleutel, soort, nummer, nu=None):
    """Hoort dit kaartje bij deze knop en is het nog geen twaalf uur oud?"""
    try:
        tijdstempel_tekst, handtekening = str(kaartje or '').split('.', 1)
        tijdstempel = int(tijdstempel_tekst)
    except (ValueError, AttributeError):
        return False
    nu = nu if nu is not None else time.time()
    leeftijd = nu - tijdstempel
    if leeftijd < -300 or leeftijd > GELDIG_UREN * 3600:
        return False
    verwacht = _handtekening(sleutel, soort, nummer, tijdstempel)
    return hmac.compare_digest(verwacht, handtekening)


def buiten_europa(headers):
    """Kwam dit verzoek binnen via een Railway-knooppunt buiten Europa?

    Tweede slot naast het kaartje. Railway zet het knooppunt in de kop
    X-Railway-Edge ("europe-west4-drams3a"); Nederlandse bezoekers komen
    altijd via Europa binnen, het botnet van 3 oktober via us-west2.
    Ontbreekt de kop, dan is het antwoord False: liever een robot te veel
    door dan een klant tegengehouden.
    """
    knooppunt = (headers.get('X-Railway-Edge') or '').lower()
    return bool(knooppunt) and 'europe' not in knooppunt
