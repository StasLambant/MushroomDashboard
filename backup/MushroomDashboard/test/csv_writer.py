import csv
import time
from datetime import datetime

# File path for storing the sensor data
CSV_FILE = "sensor_data.csv"

def initialize_csv():
    """
    Initialize the CSV file with headers if it doesn't already exist.
    """
    try:
        with open(CSV_FILE, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "temperature", "humidity"])  # Add headers
    except FileExistsError:
        pass  # File already exists, no need to reinitialize

def write_to_csv(data):
    """
    Write a single row of sensor data to the CSV file.
    """
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data['date'], data['temperature'], data['humidity']])

def start_csv_writer(fetch_data_callback, interval=10):
    """
    Periodically fetch data from the main app and write it to the CSV file.

    :param fetch_data_callback: Function to fetch the latest sensor data.
    :param interval: Time in seconds between writing to the CSV file.
    """
    initialize_csv()  # Ensure CSV file is ready
    while True:
        data = fetch_data_callback()
        if data and data["temperature"] is not None and data["humidity"] is not None:
            write_to_csv(data)
            print(f"Data written to CSV: {data}")
        time.sleep(interval)
