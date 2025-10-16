from flask import Flask
from backend.api.trip_endpoints import trips_bp
from backend.api.insights_endpoints import insights_bp
from backend.config.db_connection import get_db_connection
from backend.utils.db_insert import insert_all_from_cleaned


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    app.register_blueprint(trips_bp, url_prefix='/api/trips')
    app.register_blueprint(insights_bp, url_prefix='/api/insights')

    @app.route('/')
    def home():
        return {
            "message": "Welcome to NYC Mobility API",
            "endpoints": {
                "trips": "/api/trips",
                "insights": "/api/insights"
            }
        }

    return app


if __name__ == '__main__':
    try:
        conn = get_db_connection()
        if conn is None:
            raise RuntimeError("Database connection failed")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM trips")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        if count == 0:
            inserted = insert_all_from_cleaned()
            print(
                f"Auto-ingest completed. Inserted {inserted} rows from data/cleaned.")
    except Exception as e:
        print(f"Auto-ingest skipped due to error: {e}")

    app = create_app()
    app.run(debug=True)
