import time
from app import create_app, db

app = create_app()

def init_db_with_retry(retries=10, delay=5):
    for attempt in range(retries):
        try:
            with app.app_context():
                db.create_all()
                print("Database tables created successfully!")
                return
        except Exception as e:
            print(f"Attempt {attempt + 1}/{retries} - DB not ready: {e}")
            time.sleep(delay)
    raise Exception("Could not connect to database after multiple retries")

if __name__ == '__main__':
    init_db_with_retry()
    app.run(host='0.0.0.0', port=5000, debug=True)