import sqlite3
import time
from datetime import datetime
import get_sensor_data  # Import the new sensor data module

DB_FILE = "sensor_data.db"

def initialize_database():
    """Initialize the SQLite database and create the table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                humidity REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def store_sensor_data(fetch_sensor_data, get_humidifier_state):
    #Continuously store sensor data into the database every 10 seconds (fetch_sensor_data) and log the humidifier state (get_humidifier_state).

    while True:
        try:
            sensor_data = fetch_sensor_data()
            humidifier_state = get_humidifier_state()

            if sensor_data["temperature"] is not None and sensor_data["humidity"] is not None:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sensor_data (temperature, humidity, humidifier_state)
                    VALUES (?, ?, ?)
                ''', (sensor_data["temperature"], sensor_data["humidity"], humidifier_state))
                conn.commit()
                print("Sensor data and humidifier state written to database.")
        except sqlite3.Error as db_error:
            print(f"Database error: {db_error}")
        except Exception as e:
            print(f"Unexpected error while writing to database: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
        time.sleep(10)  # Store data every 10 seconds

def get_sensor_data_for_period(start_time, end_time):
    """
    Query the database for sensor data within a time period.

    Args:
        start_time (datetime): The start time of the period.
        end_time (datetime): The end time of the period.

    Returns:
        tuple: Lists of temperatures and humidities within the specified time range.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Convert datetime objects to string format
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        # Execute SQL query to fetch data in the specified time range
        cursor.execute('''
            SELECT temperature, humidity, timestamp 
            FROM sensor_data
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (start_time_str, end_time_str))

        rows = cursor.fetchall()

        # Separate temperatures and humidities into lists
        temperature_data = [row[0] for row in rows]
        humidity_data = [row[1] for row in rows]

        return temperature_data, humidity_data

    except sqlite3.Error as db_error:
        print(f"Database error: {db_error}")
        return [], []
    except Exception as e:
        print(f"Unexpected error while fetching data: {e}")
        return [], []
    finally:
        if 'conn' in locals() and conn:
            conn.close()
