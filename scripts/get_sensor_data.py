# get_sensor_data.py
import board
import busio
import adafruit_sht31d
from datetime import datetime

# Initialize I2C bus and sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

def get_sensor_data():
    """Fetch temperature and humidity data from the SHT3x sensor."""
    try:
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        return temperature, humidity
    except Exception as e:
        print(f"Error reading from SHT3x sensor: {e}")
        return None, None
