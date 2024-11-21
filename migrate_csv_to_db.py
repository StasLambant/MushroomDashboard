import sqlite3
import csv

# Database and CSV file paths
db_file = 'sensor_data.db'
csv_file = 'sensor_data.csv'

def migrate_csv_to_db(csv_file, db_file):
    """
    Replace all data in the 'sensor_data' table in the database with the data from the CSV file.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Clear the existing data in the 'sensor_data' table
        cursor.execute("DELETE FROM sensor_data")
        print("Cleared existing data in 'sensor_data' table.")

        # Read data from the CSV file and insert into the database
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Skip the header row
            
            # Validate CSV headers
            if header != ['timestamp', 'temperature', 'humidity']:
                raise ValueError("CSV headers do not match the expected format: ['timestamp', 'temperature', 'humidity']")
            
            # Insert rows from the CSV file
            for row in csv_reader:
                cursor.execute("""
                    INSERT INTO sensor_data (timestamp, temperature, humidity)
                    VALUES (?, ?, ?)
                """, row)

        # Commit changes and close the connection
        conn.commit()
        print("Data migrated successfully to 'sensor_data.db'.")
    except Exception as e:
        print(f"An error occurred during migration: {e}")
    finally:
        conn.close()

# Execute the migration
migrate_csv_to_db(csv_file, db_file)
