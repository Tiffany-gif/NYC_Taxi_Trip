"""
Routes for insights and analytics API endpoints
"""
from backend.config.db_connection import get_db_connection
import os
import sys
from flask import Blueprint, jsonify
import mysql.connector

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

insights_bp = Blueprint('insights', __name__)


@insights_bp.route('/stats', methods=['GET'])
def get_trip_stats():
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
