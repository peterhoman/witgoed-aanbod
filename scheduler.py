"""
APScheduler Configuration
Runs sync every 6 hours
"""

from apscheduler.schedulers.background import BackgroundScheduler
from sync_products import sync_products
from sync_mediamarkt import sync_mediamarkt
from sync_coolblue import sync_coolblue
import os

scheduler = BackgroundScheduler()

def start_scheduler():
    """Start the background scheduler (only once)"""
    # Don't start if already running
    if scheduler.running:
        print("[*] Scheduler already running")
        return

    sync_interval = int(os.getenv('SYNC_INTERVAL', 6))

    scheduler.add_job(
        sync_products,
        'interval',
        hours=sync_interval,
        id='bol_sync_job',
        name='Bol.com Product Sync',
        replace_existing=True
    )

    # De MediaMarkt-feed verandert trager en is fors groter; 2x per dag volstaat.
    mediamarkt_interval = int(os.getenv('MEDIAMARKT_SYNC_INTERVAL', 12))
    scheduler.add_job(
        sync_mediamarkt,
        'interval',
        hours=mediamarkt_interval,
        id='mediamarkt_sync_job',
        name='MediaMarkt Product Sync',
        replace_existing=True
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
        replace_existing=True
    )

    scheduler.start()
    print(f"[+] Scheduler started - Bol every {sync_interval}h, MediaMarkt every "
          f"{mediamarkt_interval}h, Coolblue every {coolblue_interval}h")

def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("[+] Scheduler stopped")
