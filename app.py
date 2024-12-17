import time
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request

import sys
import os
import json

# Add the 'scripts' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

import db_writer  # Import the database writer module
import get_sensor_data  # Import the new sensor data script
import subprocess

# Initialize Flask app
app = Flask(__name__)

VARIABLES_FILE = "variables/variables.json"

# Global variable to store sensor data
sensor_data = {
    "temperature": None,
    "humidity": None,
    "date": None
}

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

@app.route('/', methods=['GET'])
def home():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/api/variables', methods=['GET'])
def get_variables():
    try:
        # Ensure the file exists
        if not os.path.exists(VARIABLES_FILE):
            return jsonify({"error": "Variables file not found."}), 404

        # Load variables from file
        with open(VARIABLES_FILE, 'r') as file:
            variables = json.load(file)

        return jsonify(variables), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/variables', methods=['POST'])
def update_variables():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided."}), 400

        if not validate_variables(data):
            return jsonify({"error": "Invalid data. Ensure numeric values and valid ON/OFF relationship."}), 400

        with open(VARIABLES_FILE, 'w') as file:
            json.dump(data, file, indent=4)

        return jsonify({"message": "Variables updated successfully."}), 200
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

def validate_variables(data):
    try:
        if 'humidifier_on' not in data or 'humidifier_off' not in data:
            return False

        humidifier_on = data['humidifier_on']
        humidifier_off = data['humidifier_off']

        if not (isinstance(humidifier_on, (int, float)) and isinstance(humidifier_off, (int, float))):
            return False
        if round(humidifier_on, 1) != humidifier_on or round(humidifier_off, 1) != humidifier_off:
            return False

        if not humidifier_off > humidifier_on:
            return False

        return True
    except:
        return False

if __name__ == "__main__":
    # Ensure the database is initialized
    db_writer.initialize_database()

    # Start the sensor updating thread
    sensor_thread = threading.Thread(target=update_sensor_data)
    sensor_thread.daemon = True
    sensor_thread.start()

    # Start the database writer thread
    db_writer_thread = threading.Thread(
        target=db_writer.store_sensor_data, 
        args=(lambda: sensor_data,)  # Pass sensor_data via lambda for live updates
    )
    db_writer_thread.daemon = True
    db_writer_thread.start()

    # Start the humidity control subprocess
    humidity_control_path = os.path.join(os.path.dirname(__file__), 'scripts', 'humidity_control.py')
    humidity_process = subprocess.Popen(['python3', humidity_control_path])

    # Start the Flask server (accessible on your local network)
    app.run(host='0.0.0.0', port=5000)
