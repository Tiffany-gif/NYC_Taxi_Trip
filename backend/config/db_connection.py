import mysql.connector
from mysql.connector import MySQLConnection
from typing import Optional

from .db_config import get_db_config


def get_db_connection() -> Optional[MySQLConnection]:
    """Return a new MySQL connection using central config, or None on failure.

    Callers are responsible for closing the connection.
    """
    try:
        config = get_db_config()
        return mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        # Keep logging minimal here; endpoint layers can decide how to handle
        print(f"Error connecting to MySQL: {error}")
        return None
