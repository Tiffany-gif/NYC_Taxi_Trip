import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    'user': 'root',
    'password': '1mysqlS2025!',
    'host': 'localhost',
    'database': 'trip_data'
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connected to database")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Access denied")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit(1)


cursor.execute("SELECT COUNT(*) FROM vendors")
vendor_count = cursor.fetchone()[0]
print(f"Number of vendors: {vendor_count}")


cursor.execute("SELECT COUNT(*) FROM trips")
trip_count = cursor.fetchone()[0]
print(f"Number of trips: {trip_count}")


cursor.execute("SELECT * FROM trips LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()

