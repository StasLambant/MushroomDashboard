import sqlite3
import time

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

def store_sensor_data(fetch_sensor_data):
    """
    Continuously store sensor data into the database every 10 seconds.
    
    Args:
        fetch_sensor_data (function): A function that provides the latest sensor data dictionary.
    """
    while True:
        try:
            sensor_data = fetch_sensor_data()
            if sensor_data["temperature"] is not None and sensor_data["humidity"] is not None:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sensor_data (temperature, humidity)
                    VALUES (?, ?)
                ''', (sensor_data["temperature"], sensor_data["humidity"]))
                conn.commit()
                print("Sensor data written to database.")
        except sqlite3.Error as db_error:
            print(f"Database error: {db_error}")
        except Exception as e:
            print(f"Unexpected error while writing to database: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
        time.sleep(10)  # Store data every 10 seconds
