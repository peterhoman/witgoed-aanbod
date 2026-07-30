"""
APScheduler Configuration
Runs sync every 6 hours
"""

from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from sync_products import sync_products
from sync_mediamarkt import sync_mediamarkt
from sync_coolblue import sync_coolblue
from sync_expert import sync_expert
from sync_alternate import sync_alternate
from sync_ep import sync_ep
import os

scheduler = BackgroundScheduler()

def start_scheduler(app=None):
    """Start the background scheduler (only once).

    De eerstvolgende run wordt verankerd aan de laatste échte sync in de
    database (offers.last_synced) in plaats van aan de processtart. Een
    'interval'-job vuurt namelijk pas ná het hele interval, en elke deploy
    of herstart reset die klok — waardoor bij een paar deploys per dag de
    syncs stilletjes dagen konden uitblijven. Is een sync achterstallig,
    dan draait hij nu binnen enkele minuten na de start (gestaffeld, zodat
    de drie syncs elkaar niet overlappen).
    """
    # Don't start if already running
    if scheduler.running:
        print("[*] Scheduler already running")
        return

    def eerste_run(retailer, interval_uren, offset_min):
        # Tijdzone-bewust rekenen: de database bewaart naïeve UTC-tijden,
        # maar APScheduler interpreteert naïeve datetimes in de LOKALE zone.
        # Zonder expliciete UTC-markering zou een achterstallige run op een
        # niet-UTC-machine als "gemist" worden weggeschoven naar +interval.
        from models import db, Offer
        laatst = None
        if app is not None:
            try:
                with app.app_context():
                    laatst = (db.session.query(db.func.max(Offer.last_synced))
                              .filter(Offer.retailer == retailer).scalar())
            except Exception as e:
                print(f"[!] Kon laatste sync van {retailer} niet bepalen: {e}")
        nu = datetime.now(timezone.utc)
        if laatst is not None:
            laatst = laatst.replace(tzinfo=timezone.utc)
        if laatst is None or laatst + timedelta(hours=interval_uren) <= nu:
            return nu + timedelta(minutes=offset_min)  # achterstallig: zo draaien
        return laatst + timedelta(hours=interval_uren)

    sync_interval = int(os.getenv('SYNC_INTERVAL', 6))

    scheduler.add_job(
        sync_products,
        'interval',
        hours=sync_interval,
        id='bol_sync_job',
        name='Bol.com Product Sync',
        replace_existing=True,
        next_run_time=eerste_run('bol', sync_interval, 2),
    )

    # De MediaMarkt-feed verandert trager en is fors groter; 2x per dag volstaat.
    mediamarkt_interval = int(os.getenv('MEDIAMARKT_SYNC_INTERVAL', 12))
    scheduler.add_job(
        sync_mediamarkt,
        'interval',
        hours=mediamarkt_interval,
        id='mediamarkt_sync_job',
        name='MediaMarkt Product Sync',
        replace_existing=True,
        next_run_time=eerste_run('mediamarkt', mediamarkt_interval, 20),
    )

    # De Coolblue-feed is klein (~4 MB) maar verandert ook maar een paar keer
    # per dag; zelfde ritme als MediaMarkt.
    coolblue_interval = int(os.getenv('COOLBLUE_SYNC_INTERVAL', 12))
    scheduler.add_job(
        sync_coolblue,
        'interval',
        hours=coolblue_interval,
        id='coolblue_sync_job',
        name='Coolblue Product Sync',
        replace_existing=True,
        next_run_time=eerste_run('coolblue', coolblue_interval, 35),
    )

    # Expert via de TradeTracker-feed (uurlijks ververst; 2x per dag ophalen
    # volstaat ruim, zelfde ritme als de andere feed-winkels).
    expert_interval = int(os.getenv('EXPERT_SYNC_INTERVAL', 12))
    scheduler.add_job(
        sync_expert,
        'interval',
        hours=expert_interval,
        id='expert_sync_job',
        name='Expert Product Sync',
        replace_existing=True,
        next_run_time=eerste_run('expert', expert_interval, 50),
    )

    # Alternate via de TradeTracker-feed, zelfde ritme als Expert.
    alternate_interval = int(os.getenv('ALTERNATE_SYNC_INTERVAL', 12))
    scheduler.add_job(
        sync_alternate,
        'interval',
        hours=alternate_interval,
        id='alternate_sync_job',
        name='Alternate Product Sync',
        replace_existing=True,
        next_run_time=eerste_run('alternate', alternate_interval, 65),
    )

    # EP via de TradeTracker-feed, zelfde ritme als Expert/Alternate.
    ep_interval = int(os.getenv('EP_SYNC_INTERVAL', 12))
    scheduler.add_job(
        sync_ep,
        'interval',
        hours=ep_interval,
        id='ep_sync_job',
        name='EP Product Sync',
        replace_existing=True,
        next_run_time=eerste_run('ep', ep_interval, 80),
    )

    # Nieuwe producten van een eigen beschrijving voorzien. Draait na de syncs
    # (offset 95 min, de laatste sync zit op 80), zodat de producten van die
    # ronde er al zijn.
    #
    # Net als de syncs verankerd aan het laatste échte draaimoment in plaats
    # van aan de processtart. Gemeten op 28 juli: deze job stond nog op de
    # oude manier en heeft daardoor een halve dag niet gedraaid -- er werd die
    # ochtend zes keer uitgerold, en elke uitrol zette hem terug op "over 95
    # minuten". Het draaimoment komt uit teksten_bijwerken.laatste_run; de
    # syncs halen hetzelfde uit offers.last_synced (zie eerste_run hierboven).
    #
    # Bewust hier en niet achter een webadres: dan is er geen beheersleutel
    # nodig die in adresbalken en serverlogs blijft staan. De grenzen zitten in
    # teksten_bijwerken zelf -- alleen producten zonder tekst, hoogstens 25 per
    # ronde, en het dagplafond wordt voor elke tekst opnieuw getoetst.
    if app is not None:
        from teksten_bijwerken import laatste_run, vul_ontbrekende_teksten
        teksten_interval = int(os.getenv('TEKSTEN_INTERVAL', 6))
        laatst_teksten = laatste_run(app)
        nu = datetime.now(timezone.utc)
        if laatst_teksten is not None:
            laatst_teksten = laatst_teksten.replace(tzinfo=timezone.utc)
        if (laatst_teksten is None
                or laatst_teksten + timedelta(hours=teksten_interval) <= nu):
            # Achterstallig: binnen tien minuten draaien, niet over 95. Die
            # 95 minuten waren bedoeld om de syncs voor te laten gaan, maar op
            # een dag met een uitrol per half uur wordt zo'n uitgestelde run
            # nooit gehaald -- dat is precies hoe deze routine stil kwam te
            # liggen. Voorgaan is hier het minste belang: de routine schrijft
            # alleen voor producten zónder tekst en draait toch elke zes uur,
            # dus wat deze sync nog aanlevert komt vanzelf de volgende ronde.
            eerste_teksten = nu + timedelta(minutes=10)
        else:
            eerste_teksten = laatst_teksten + timedelta(hours=teksten_interval)
        scheduler.add_job(
            vul_ontbrekende_teksten,
            'interval',
            hours=teksten_interval,
            id='teksten_job',
            name='Eigen productteksten bijwerken',
            replace_existing=True,
            args=[app],
            next_run_time=eerste_teksten,
        )

    # EPREL-gegevens ophalen bij de EU-energielabeldatabase. Kost niets en
    # heeft geen sleutel nodig; de grenzen zitten in eprel_bijwerken zelf
    # (honderd apparaten per ronde, een halve seconde tussen de verzoeken,
    # en een misser wordt vastgelegd zodat hij niet elke ronde terugkomt).
    #
    # Verankerd aan het laatste draaimoment, om dezelfde reden als de andere
    # jobs hierboven: een interval-job die aan de processtart hangt schuift
    # bij elke uitrol vooruit en draait op een drukke dag niet meer.
    if app is not None:
        from eprel_bijwerken import vul_eprel_gegevens
        from models import EprelData
        # Drie uur zolang de catalogus nog gevuld wordt: dat halveert de
        # doorlooptijd van ruim zeven dagen naar ruim drie. Bewust niet
        # korter -- EPREL publiceert geen limieten, dus we weten niet waar de
        # grens ligt, en de toegang kwijtraken kost meer dan een paar dagen
        # winnen oplevert. Loopt het toch tegen een afwijzing aan, dan stopt
        # de ronde bij het eerste geweigerde verzoek en staat de reden in
        # /api/eprel onder laatste_ronde_afloop.
        eprel_interval = int(os.getenv('EPREL_INTERVAL', 3))
        laatst_eprel = None
        try:
            with app.app_context():
                rij = (EprelData.query
                       .order_by(EprelData.opgehaald_at.desc()).first())
                laatst_eprel = rij.opgehaald_at if rij else None
        except Exception as e:
            print(f"[!] Kon laatste EPREL-ronde niet bepalen: {e}")
        nu_eprel = datetime.now(timezone.utc)
        if laatst_eprel is not None:
            laatst_eprel = laatst_eprel.replace(tzinfo=timezone.utc)
        if (laatst_eprel is None
                or laatst_eprel + timedelta(hours=eprel_interval) <= nu_eprel):
            eerste_eprel = nu_eprel + timedelta(minutes=12)
        else:
            eerste_eprel = laatst_eprel + timedelta(hours=eprel_interval)
        scheduler.add_job(
            vul_eprel_gegevens,
            'interval',
            hours=eprel_interval,
            id='eprel_job',
            name='EPREL-gegevens bijwerken',
            replace_existing=True,
            args=[app],
            next_run_time=eerste_eprel,
        )

    # Geblokkeerde artikelen opruimen en setjes in hun eigen categorie zetten.
    # Elk uur, want de syncs lezen de feeds opnieuw en zetten een geblokkeerd
    # artikel er zo weer in. Kost een paar query's.
    if app is not None:
        from catalogus_uitzonderingen import pas_toe as uitzonderingen_toepassen
        scheduler.add_job(
            uitzonderingen_toepassen,
            'interval',
            hours=1,
            id='uitzonderingen_job',
            name='Catalogusuitzonderingen toepassen',
            replace_existing=True,
            args=[app],
            next_run_time=datetime.now(timezone.utc) + timedelta(minutes=3),
        )

    scheduler.start()
    for job in scheduler.get_jobs():
        print(f"[+] {job.name}: eerstvolgende run {job.next_run_time}")
    print(f"[+] Scheduler started - Bol every {sync_interval}h, MediaMarkt every "
          f"{mediamarkt_interval}h, Coolblue every {coolblue_interval}h")

def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("[+] Scheduler stopped")
