from app import create_app
from scheduler import start_scheduler

app = create_app()

# Start scheduler in production
if __name__ != '__main__':
    start_scheduler()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
