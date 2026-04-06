# Provides temperature, humidity, and CO2 sensor readings via I2C sensors (SHT31 and SCD41).

import board
import busio
import adafruit_sht31d
import adafruit_scd4x
from datetime import datetime

try:
    import spidev
    spi = spidev.SpiDev()
    spi.open(0, 0)   # bus 0, CE0
    spi.max_speed_hz = 5000000
    spi.mode = 0
    SPI_AVAILABLE = True
except (ImportError, FileNotFoundError, OSError):
    SPI_AVAILABLE = False
    spi = None

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
    """Fetch CO2 and relative humidity data from the SCD4x sensor."""
    try:
        co2 = scd4x.CO2
        scd41_humidity = scd4x.relative_humidity  # Fetch relative humidity from SCD41
        # Add check for max spike (32774 is known error value)
        if co2 is not None and 400 <= co2 <= 10000:
            last_valid_co2 = round(co2, 0)
        else:
            print(f"Ignored invalid CO₂ reading: {co2}")

        print(f"SCD41 CO₂: {co2}, SCD41 Relative Humidity: {scd41_humidity}")
        return last_valid_co2
    except Exception as e:
        print(f"CO2 read error: {e}")
        return last_valid_co2

def get_thermocouple_temp():
    """Fetch temperature from the MAX31855 thermocouple."""
    if not SPI_AVAILABLE:
        return None
    try:
        # Read 4 bytes from the MAX31855
        raw = spi.xfer2([0x00, 0x00, 0x00, 0x00])
        value = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]

        # Check for fault
        if value & 0x7:
            # Bit 2: SCV, bit 1: SCG, bit 0: OC
            print("Thermocouple fault, status bits:", value & 0x7)
            return None

        # Thermocouple temperature (bits 31..18, signed, 0.25°C units)
        tc_raw = value >> 18  # shift down so bit 13 is sign bit
        if tc_raw & 0x2000:   # sign bit set?
            tc_raw -= 0x4000  # sign-extend negative value
        tc_temp_c = tc_raw * 0.25

        return tc_temp_c
    except Exception as e:
        print(f"Error reading thermocouple: {e}")
        return None
