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
    # Bewust hier en niet achter een webadres: dan is er geen beheersleutel
    # nodig die in adresbalken en serverlogs blijft staan. De grenzen zitten in
    # teksten_bijwerken zelf -- alleen producten zonder tekst, hoogstens 25 per
    # ronde, en het dagplafond wordt voor elke tekst opnieuw getoetst.
    if app is not None:
        from teksten_bijwerken import vul_ontbrekende_teksten
        teksten_interval = int(os.getenv('TEKSTEN_INTERVAL', 6))
        scheduler.add_job(
            vul_ontbrekende_teksten,
            'interval',
            hours=teksten_interval,
            id='teksten_job',
            name='Eigen productteksten bijwerken',
            replace_existing=True,
            args=[app],
            next_run_time=datetime.now(timezone.utc) + timedelta(minutes=95),
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
