import sqlite3
from datetime import datetime

DB_FILE = "/home/slambant1/Desktop/MushroomDashboard/sensor_data.db"

def normalize_timestamps():
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Query to select all records where the timestamp has slashes in the format
        cursor.execute("SELECT id, timestamp FROM sensor_data WHERE timestamp LIKE '%/%'")
        records = cursor.fetchall()

        print(f"Found {len(records)} records with incorrect timestamp format.")

        for record in records:
            record_id, timestamp = record
            try:
                # Attempt to parse the timestamp in the incorrect format (with slashes)
                parsed_time = datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S")
                # Convert to the correct format (with dashes)
                corrected_time = parsed_time.strftime("%Y-%m-%d %H:%M:%S")

                # Update the record in the database
                cursor.execute(
                    "UPDATE sensor_data SET timestamp = ? WHERE id = ?",
                    (corrected_time, record_id),
                )
                print(f"Updated record {record_id} with new timestamp: {corrected_time}")
            except ValueError:
                print(f"Skipping unrecognized timestamp format for ID {record_id}: {timestamp}")

        # Commit the changes to the database
        conn.commit()
        print("Timestamps normalization completed successfully.")
    except sqlite3.Error as db_error:
        print(f"Database error: {db_error}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# Call the function to normalize timestamps
normalize_timestamps()
