# Writes sensor readings and humidifier state into SQLite database on a timed interval.

import sqlite3
import time
from zoneinfo import ZoneInfo  # Use zoneinfo for time zone handling
from datetime import datetime
import get_sensor_data  # Import the new sensor data module.

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
                co2 REAL,
                thermocouple REAL,
                humidifier_state TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                
            )
        ''')
        # Add thermocouple column if it doesn't exist (for migration)
        try:
            cursor.execute("ALTER TABLE sensor_data ADD COLUMN thermocouple REAL")
        except sqlite3.OperationalError:
            pass  # Column already exists
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def store_sensor_data(fetch_sensor_data, get_humidifier_state, get_co2_data):
    """
    Continuously store sensor data into the database every 10 seconds, averaging thermocouple readings over the period.

    Args:
        fetch_sensor_data (function): A function that provides the latest sensor data dictionary.
        get_humidifier_state (function): A function that provides the current humidifier state.
    """
     # Define the local time zone (UTC+1)
    local_tz = ZoneInfo('Europe/London')  # Adjust to local time zone

    while True:
        try:
            thermocouple_readings = []
            last_sensor_data = None
            last_co2_data = None
            last_humidifier_state = None
            
            # Collect 10 readings over 10 seconds
            for _ in range(10):
                sensor_data = fetch_sensor_data()
                humidifier_state = get_humidifier_state()
                co2_data = get_co2_data()
                
                if sensor_data["thermocouple"] is not None:
                    thermocouple_readings.append(sensor_data["thermocouple"])
                
                # Keep the last values for other data
                last_sensor_data = sensor_data
                last_co2_data = co2_data
                last_humidifier_state = humidifier_state
                
                time.sleep(1)
            
            # Calculate average thermocouple if we have readings
            avg_thermocouple = None
            if thermocouple_readings:
                avg_thermocouple = sum(thermocouple_readings) / len(thermocouple_readings)
            
            if last_sensor_data and last_sensor_data["temperature"] is not None and last_sensor_data["humidity"] is not None:
                # Get the current time in the local time zone
                local_time = datetime.now(local_tz)
                local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')

                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sensor_data (temperature, humidity, humidifier_state, co2, thermocouple, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    last_sensor_data["temperature"], 
                    last_sensor_data["humidity"],
                    last_humidifier_state,
                    last_co2_data,
                    round(avg_thermocouple, 2) if avg_thermocouple is not None else None,
                    local_time_str
                ))
                conn.commit()
                print(f"Sensor data written to database. Thermocouple avg: {avg_thermocouple:.2f} from {len(thermocouple_readings)} readings.")
        except sqlite3.Error as db_error:
            print(f"Database error: {db_error}")
        except Exception as e:
            print(f"Unexpected error while writing to database: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()

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
        print(f"Error fetching SHT3x data: {e}")
        return [], []
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def get_co2_data_for_period(start_time, end_time):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            SELECT co2 FROM sensor_data
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (start_str, end_str))

        co2_values = [row[0] for row in cursor.fetchall()]
        return co2_values

    except Exception as e:
        print(f"Error fetching CO2 data: {e}")
        return []
    finally:
        conn.close()

def get_thermocouple_data_for_period(start_time, end_time):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            SELECT thermocouple FROM sensor_data
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (start_str, end_str))

        thermocouple_values = [row[0] for row in cursor.fetchall()]
        return thermocouple_values

    except Exception as e:
        print(f"Error fetching thermocouple data: {e}")
        return []
    finally:
        conn.close()

