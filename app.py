import time
import board
import busio
import adafruit_sht31d
from flask import Flask, jsonify, render_template
import threading
from datetime import datetime, timedelta
import db_writer  # Import the database writer module

# Initialize Flask app
app = Flask(__name__)

# Initialize I2C bus and sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

# Global variable to store sensor data
sensor_data = {
    "temperature": None,
    "humidity": None,
    "date": None
}

def get_sensor_data():
    """Fetch temperature and humidity data from SHT3x sensor."""
    try:
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        return temperature, humidity
    except Exception as e:
        print(f"Error reading from SHT3x sensor: {e}")
        return None, None

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

def update_sensor_data():
    """Continuously update sensor data every second."""
    global sensor_data
    while True:
        temperature, humidity = get_sensor_data()
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

    # Start the database writer thread
    db_writer_thread = threading.Thread(
        target=db_writer.store_sensor_data, 
        args=(lambda: sensor_data,)  # Pass sensor_data via lambda for live updates
    )
    db_writer_thread.daemon = True
    db_writer_thread.start()

    # Start the Flask server (accessible on your local network)
    app.run(host='0.0.0.0', port=5000)
