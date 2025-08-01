# get_sensor_data.py
import board
import busio
import adafruit_sht31d
import adafruit_scd4x
from datetime import datetime

# Initialize I2C bus and sensor
i2c = busio.I2C(board.SCL, board.SDA)

#initialize SHT3x sensor (temperature and humidity)
sht31 = adafruit_sht31d.SHT31D(i2c)
# Initialize SCD4x sensor (CO2, temperature, humidity)
scd4x = adafruit_scd4x.SCD4X(i2c)
scd4x.start_periodic_measurement()  # Start periodic measurement for SCD4x

def get_sensor_data():
    """Fetch temperature and humidity data from the SHT3x sensor."""
    try:
        temperature = sht31.temperature
        humidity = sht31.relative_humidity
        return temperature, humidity
    except Exception as e:
        print(f"Error reading from SHT3x sensor: {e}")
        return None, None

# Global variable to store last good CO2 value
last_valid_co2 = None

def get_co2():
    global last_valid_co2
    """Fetch CO2 data from the SCD4x sensor."""
    try:
        co2 = scd4x.CO2
        if co2 is not None:
            last_valid_co2 = round(co2, 0)
        return last_valid_co2
    except Exception as e:
        print(f"CO2 read error: {e}")
        return last_valid_co2
