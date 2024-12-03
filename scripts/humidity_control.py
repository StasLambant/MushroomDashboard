import RPi.GPIO as GPIO
import time
import sys
import os

# Add the 'scripts' folder to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Import get_sensor_data
import get_sensor_data  # Now using the get_sensor_data module to fetch sensor data

# Constants
RELAY_PIN = 26  # GPIO pin for Relay 1 (connected to pin 37)
HUMIDITY_THRESHOLD_ON = 88.25  # The humidity value above which relay will be turned ON
HUMIDITY_THRESHOLD_OFF = 88.22  # The humidity value below which relay will be turned OFF

# Initialize GPIO settings
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Set relay pin as output

def check_and_control_relay():
    """
    This function will check the current humidity from the sensor and control the relay.
    """
    try:
        # Fetch the latest temperature and humidity from the sensor
        temperature, humidity = get_sensor_data.get_sensor_data()  # Get temperature and humidity from the sensor

        if humidity is not None:
            print(f"Current Humidity: {humidity}%")
            
            # Switch relay ON if humidity is above threshold
            if humidity > HUMIDITY_THRESHOLD_ON:
                if GPIO.input(RELAY_PIN) == GPIO.HIGH:  # If relay is off, turn it on
                    GPIO.output(RELAY_PIN, GPIO.LOW)
                    print("Relay ON - Humidity is above threshold.")
            
            # Switch relay OFF if humidity is below threshold
            elif humidity < HUMIDITY_THRESHOLD_OFF:
                if GPIO.input(RELAY_PIN) == GPIO.LOW:  # If relay is on, turn it off
                    GPIO.output(RELAY_PIN, GPIO.HIGH)
                    print("Relay OFF - Humidity is below threshold.")
        else:
            print("Failed to get humidity data.")

    except Exception as e:
        print(f"Error in controlling relay: {e}")

def run_relay_control():
    """Continuously monitor the humidity and control relay based on thresholds."""
    try:
        while True:
            check_and_control_relay()
            time.sleep(5)  # Check every 5 seconds (you can adjust the sleep time)

    except KeyboardInterrupt:
        print("Relay control stopped.")
    finally:
        GPIO.cleanup()  # Cleanup GPIO settings when done

if __name__ == "__main__":
    run_relay_control()
