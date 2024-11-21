import sqlite3

DB_FILE = 'sensor_data.db'

def initialize_database():
    """Initialize the SQLite database and create the table with an id column."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Drop the table if it already exists to recreate with the correct schema
    cursor.execute('DROP TABLE IF EXISTS sensor_data')

    # Create the table with an id column as the primary key
    cursor.execute('''
        CREATE TABLE sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
    print("Database initialized successfully!")
