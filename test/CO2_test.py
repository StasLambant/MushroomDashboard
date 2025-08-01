#!/usr/bin/env python3

import time
import board
import adafruit_scd4x

def main():
    # Initialize I2C bus on Pi's default SCL/SDA pins
    i2c = board.I2C()

    # Create sensor object
    scd = adafruit_scd4x.SCD4X(i2c)
    print("Serial number:", [hex(i) for i in scd.serial_number])

    # Start periodic measurement
    scd.start_periodic_measurement()
    print("Waiting for first measurement…")

    # Loop and print readings
    while True:
        if scd.data_ready:  # Check if new data is available
            print(f"CO₂: {scd.CO2} ppm")
            print(f"Temp: {scd.temperature:.1f} °C")
            print(f"Humidity: {scd.relative_humidity:.1f} %")
            print("-" * 30)
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Measurement stopped by user")
