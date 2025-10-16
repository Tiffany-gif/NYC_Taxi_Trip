"""
Routes for insights and analytics API endpoints
"""
from utils.efficiency_algorithm import rank_trips_by_efficiency
from config.db_config import get_db_config
import os
import sys
from flask import Blueprint, jsonify, request
import mysql.connector


backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

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


@insights_bp.route('/top-efficient-trips', methods=['POST'])
def top_efficient_trips():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, trip_distance_km, trip_duration_min, fare_amount FROM trips LIMIT 100")
        trips = cursor.fetchall()
        ranked_trips = rank_trips_by_efficiency(trips)
        cursor.close()
        conn.close()
        return jsonify(ranked_trips[:10])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@insights_bp.route('/stats', methods=['GET'])
def get_trip_stats():
    """Get statistics about the trips data"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor(dictionary=True)

        stats = {}

        cursor.execute("SELECT COUNT(*) as count FROM trips")
        stats["total_trips"] = cursor.fetchone()['count']

        cursor.execute(
            "SELECT AVG(trip_duration_min) as avg_duration FROM trips")
        stats["avg_duration_min"] = cursor.fetchone()['avg_duration']

        cursor.execute("SELECT AVG(speed_kmh) as avg_speed FROM trips")
        stats["avg_speed_kmh"] = cursor.fetchone()['avg_speed']

        cursor.execute(
            "SELECT AVG(trip_distance_km) as avg_distance FROM trips")
        stats["avg_distance_km"] = cursor.fetchone()['avg_distance']

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
