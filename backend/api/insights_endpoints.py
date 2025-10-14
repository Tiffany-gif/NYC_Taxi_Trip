"""
Routes for insights and analytics API endpoints
"""
from config.db_config import get_db_config
import os
import sys
from flask import Blueprint, jsonify, request
import mysql.connector

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Create a Blueprint for insights routes
insights_bp = Blueprint('insights', __name__)


def get_db_connection():
    """Helper function to get a database connection"""
    try:
        config = get_db_config()
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


@insights_bp.route('/stats', methods=['GET'])
def get_trip_stats():
    """Get statistics about the trips data"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor(dictionary=True)

        # Get various statistics
        stats = {}

        # Total number of trips
        cursor.execute("SELECT COUNT(*) as count FROM trips")
        stats["total_trips"] = cursor.fetchone()['count']

        # Average trip duration (minutes)
        cursor.execute(
            "SELECT AVG(trip_duration_min) as avg_duration FROM trips")
        stats["avg_duration_min"] = cursor.fetchone()['avg_duration']

        # Average speed
        cursor.execute("SELECT AVG(speed_kmh) as avg_speed FROM trips")
        stats["avg_speed_kmh"] = cursor.fetchone()['avg_speed']

        # Average distance
        cursor.execute(
            "SELECT AVG(trip_distance_km) as avg_distance FROM trips")
        stats["avg_distance_km"] = cursor.fetchone()['avg_distance']

        # Most common passenger count
        cursor.execute("""
            SELECT passenger_count, COUNT(*) as count 
            FROM trips 
            GROUP BY passenger_count 
            ORDER BY count DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        stats["most_common_passenger_count"] = result['passenger_count'] if result else None

        cursor.close()
        conn.close()

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@insights_bp.route('/hourly-pattern', methods=['GET'])
def get_hourly_pattern():
    """Get trip counts by hour of day"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor(dictionary=True)

        # Extract hour from pickup_datetime and count trips
        query = """
        SELECT HOUR(pickup_datetime) as hour, COUNT(*) as trip_count 
        FROM trips 
        GROUP BY HOUR(pickup_datetime)
        ORDER BY hour
        """
        cursor.execute(query)
        hourly_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(hourly_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
