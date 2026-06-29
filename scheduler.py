"""
APScheduler Configuration
Runs sync every 6 hours
"""

from apscheduler.schedulers.background import BackgroundScheduler
from sync_products import sync_products
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

    scheduler.start()
    print(f"[+] Scheduler started - sync every {sync_interval} hours")

def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("[+] Scheduler stopped")
