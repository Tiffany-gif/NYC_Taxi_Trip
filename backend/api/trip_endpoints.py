"""
Routes for trip data API endpoints
"""
from backend.config.db_connection import get_db_connection
import os
import sys
from flask import Blueprint, jsonify, request
import mysql.connector
from backend.utils.db_insert import insert_from_csv, insert_dataframe

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Create a Blueprint for trips routes
trips_bp = Blueprint('trips', __name__)

@trips_bp.route('/', methods=['GET'])
def get_trips():
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)
        min_speed = request.args.get('min_speed', default=0, type=float)
        max_speed = request.args.get('max_speed', type=float)

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM trips WHERE 1=1"
        params = []

        if min_speed is not None:
            query += " AND speed_kmh >= %s"
            params.append(min_speed)

        if max_speed is not None:
            query += " AND speed_kmh <= %s"
            params.append(max_speed)

        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        trips = cursor.fetchall()

        count_query = "SELECT COUNT(*) as count FROM trips WHERE 1=1"
        count_params = []

        if min_speed is not None:
            count_query += " AND speed_kmh >= %s"
            count_params.append(min_speed)
        if max_speed is not None:
            count_query += " AND speed_kmh <= %s"
            count_params.append(max_speed)

        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        return jsonify({
            "trips": trips,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@trips_bp.route('/ingest', methods=['POST'])
def ingest_trips():
    """Ingest trips from CSV (path in JSON body optional: {"csv_path": "..."})."""
    try:
        data = request.get_json(silent=True) or {}
        csv_path = data.get('csv_path') if isinstance(data, dict) else None
        inserted = insert_from_csv(csv_path)
        return jsonify({"inserted": inserted}), 201
    except FileNotFoundError:
        return jsonify({"error": "CSV file not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@trips_bp.route('/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM trips WHERE id = %s"
        cursor.execute(query, (trip_id,))
        trip = cursor.fetchone()

        cursor.close()
        conn.close()

        if trip:
            return jsonify(trip)
        else:
            return jsonify({"error": "Trip not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Testing database connection...")
    conn = get_db_connection()
    if conn:
        print("Database connection successful!")
        conn.close()
    else:
        print("Database connection failed!")

