from app import create_app
import os

app = create_app()

# Start scheduler only in production. Geen WERKZEUG_RUN_MAIN-check: die
# variabele bestaat alleen onder de Flask dev-reloader, nooit onder gunicorn,
# waardoor de scheduler in productie stilletjes nooit startte. Gunicorn draait
# hier met 1 worker (Procfile/railway.toml), dus geen dubbele schedulers.
if os.getenv('FLASK_ENV') == 'production':
    from scheduler import start_scheduler
    try:
        start_scheduler(app)
    except Exception as e:
        print(f"[!] Scheduler start error: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
