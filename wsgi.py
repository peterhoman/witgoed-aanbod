from app import create_app
import os

app = create_app()

# Start scheduler only once in production (on master process)
if os.getenv('FLASK_ENV') == 'production' and os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    from scheduler import start_scheduler
    start_scheduler()

if __name__ == '__main__':
    from scheduler import start_scheduler
    start_scheduler()
    app.run(debug=True, host='0.0.0.0', port=5000)
