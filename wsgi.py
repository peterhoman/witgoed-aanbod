from app import create_app
import os

app = create_app()

# Start de scheduler in productie. Niet alleen op FLASK_ENV vertrouwen:
# /api/sync-status liet zien dat die variabele op Railway ontbreekt,
# waardoor er nooit een sync was ingepland (scheduler_jobs: []) en alle
# syncs ooit handmatig bleken. Railway injecteert zelf altijd
# RAILWAY_ENVIRONMENT; lokaal (python wsgi.py / dev-server) blijven
# beide leeg en start er dus geen scheduler. Gunicorn draait hier met
# 1 worker (Procfile/railway.toml), dus geen dubbele schedulers.
if os.getenv('FLASK_ENV') == 'production' or os.getenv('RAILWAY_ENVIRONMENT'):
    from scheduler import start_scheduler
    try:
        start_scheduler(app)
    except Exception as e:
        print(f"[!] Scheduler start error: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
