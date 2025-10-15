import os

try:
    # Optional: load variables from project root .env if python-dotenv is installed
    from dotenv import load_dotenv  # type: ignore
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except Exception:
    # Silently ignore if dotenv is not installed; rely on environment
    pass


def get_db_config():
    return {
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'database': os.environ.get('DB_NAME', 'trip_data')
    }
