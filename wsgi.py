from app import create_app
import os

app = create_app()

# Start scheduler only in production (avoid multiple starts in reloader)
if os.getenv('FLASK_ENV') == 'production':
    # Only start on main process, not in reloader
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from scheduler import start_scheduler
        try:
            start_scheduler()
        except Exception as e:
            print(f"[!] Scheduler start error: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
