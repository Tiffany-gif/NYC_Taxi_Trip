import mysql.connector
from mysql.connector import MySQLConnection
from typing import Optional, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "nyc_user"),
        "password": os.getenv("DB_PASSWORD", "nyc123!"),
        "database": os.getenv("DB_NAME", "trip_data"),
    }

def get_db_connection() -> Optional[MySQLConnection]:
    """Return a new MySQL connection using config."""
    try:
        config = get_db_config()
        
        conn = mysql.connector.connect(**config)
        print("connected to DB")
        return conn
    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL: {error}")
        return None

def get_db_cursor() -> Tuple[Optional[MySQLConnection], Optional[mysql.connector.cursor.MySQLCursor]]:
    """Return a connection and a dictionary cursor (if connection works)."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        return conn, cursor
    return None, None
