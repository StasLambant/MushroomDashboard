import time
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request
import json
import sys
import os
import RPi.GPIO as GPIO  # Import GPIO module
import atexit

# Add the 'scripts' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

import db_writer  # Import the database writer module
import get_sensor_data  # Import the new sensor data script
import humidity_control  # Import the humidity control script

# Initialize Flask app
app = Flask(__name__)

# Global variable to store sensor data
sensor_data = {
    "temperature": None,
    "humidity": None,
    "date": None
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'variables/variables.json')
RELAY_PIN = humidity_control.RELAY_PIN  # Get the relay pin from the humidity_control module

# Cleanup GPIO on exit
def cleanup_gpio():
    print("Cleaning up GPIO...")
    humidity_control.stop_relay_control()  # Signal the humidity control thread to stop
    time.sleep(1)  # Give the thread time to stop
    GPIO.cleanup()

atexit.register(cleanup_gpio)

def load_config():
    """Load configuration settings from variables.json."""
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {"upper": 88.22, "lower": 85.00, "debounce_delay": 15, "sensor_fail_limit": 10}

def save_config(data):
    """Save updated configuration settings to variables.json."""
    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving configuration: {e}")

@app.route('/sensor_data', methods=['GET'])
def fetch_sensor_data():
    """Serve the latest sensor data as JSON."""
    return jsonify(sensor_data)

@app.route('/sensor_data/1day', methods=['GET'])
def fetch_sensor_data_1day():
    """Serve sensor data for the last 1 day."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    temperature_data, humidity_data = db_writer.get_sensor_data_for_period(start_time, end_time)
    return jsonify({
        "temperature": temperature_data,
        "humidity": humidity_data
    })

@app.route('/sensor_data/7day', methods=['GET'])
def fetch_sensor_data_7day():
    """Serve sensor data for the last 7 days."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    temperature_data, humidity_data = db_writer.get_sensor_data_for_period(start_time, end_time)
    return jsonify({
        "temperature": temperature_data,
        "humidity": humidity_data
    })

@app.route('/config', methods=['GET'])
def get_config():
    return jsonify(load_config())


@app.route('/config', methods=['POST'])#
def update_config():
    """Update the configuration settings."""
    try:
        new_config = request.json
        save_config(new_config)
        return jsonify({"message": "Configuration updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/relay_state', methods=['GET'])
def fetch_relay_state():
    """Return the current state of the relay."""
    try:
        relay_state = GPIO.input(RELAY_PIN)  # Read the current state of the relay pin
        return jsonify({"relay_state": relay_state})  # Return the raw GPIO value (0 or 1)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_sensor_data():
    """Continuously update sensor data every second."""
    global sensor_data
    while True:
        temperature, humidity = get_sensor_data.get_sensor_data()  # Fetch sensor data from the get_sensor_data module
        if temperature is not None and humidity is not None:
            # Get the current date and time in the specified format
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            sensor_data = {
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "date": current_time  # Add date to the sensor data
            }
            print(f"Updated sensor data: {sensor_data}")
        time.sleep(1)  # sampling rate

if __name__ == "__main__":
    # Ensure the database is initialized
    db_writer.initialize_database()

    # Start the sensor updating thread
    sensor_thread = threading.Thread(target=update_sensor_data)
    sensor_thread.daemon = True
    sensor_thread.start()
    print("Sensor data thread started.")

    # Start the database writer thread
    db_writer_thread = threading.Thread(
        target=db_writer.store_sensor_data, 
        args=(lambda: sensor_data, humidity_control.get_relay_state)  # Pass sensor_data via lambda for live updates and get_relay_state for logging realy state 
    )
    db_writer_thread.daemon = True
    db_writer_thread.start()
    print("Database writer thread started.")

    # Start the humidity control thread
    humidity_control_thread = threading.Thread(target=humidity_control.run_relay_control)
    humidity_control_thread.daemon = True  # Mark the thread as a daemon so it exits with the main program
    humidity_control_thread.start()
    print("Humidity control thread started.")

    # Start the Flask server (accessible on your local network)
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000)