import RPi.GPIO as GPIO
import time
import sys
import os
import json

# Add the 'scripts' folder to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Import get_sensor_data
import get_sensor_data  # Now using the get_sensor_data module to fetch sensor data

# Constants
RELAY_PIN = 26  # GPIO pin for Relay 1 (connected to pin 37)
VARIABLES_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'variables', 'variables.json')  # Path to the JSON file

# Initialize GPIO settings. All relays are lo-active, hence the reverse HIGH-LOW logic
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Relay initially OFF

def load_thresholds_from_json():
    """
    Load the humidifier ON/OFF thresholds from the variables.json file.
    """
    try:
        with open(VARIABLES_FILE_PATH, 'r') as f:
            variables = json.load(f)
            
        humidifier_on = variables.get('humidifier_on', 40)  # Default to 40 if not found
        humidifier_off = variables.get('humidifier_off', 60)  # Default to 60 if not found
        
        print(f"Loaded thresholds: Humidifier ON = {humidifier_on}, Humidifier OFF = {humidifier_off}")
        return humidifier_on, humidifier_off
    except Exception as e:
        print(f"Error loading thresholds from JSON file: {e}")
        # Fallback to default values if there's an error
        return 40, 60

def check_and_control_relay(humidifier_on, humidifier_off):
    """
    This function will check the current humidity from the sensor and control the relay.
    """
    try:
        # Fetch the latest temperature and humidity from the sensor
        temperature, humidity = get_sensor_data.get_sensor_data()  # Get temperature and humidity from the sensor

        if humidity is not None:
            print(f"Current Humidity: {humidity}%")
            
            # Turn relay ON if humidity is below humidifier_on threshold
            if humidity < humidifier_on:
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn relay ON (lo-active)
                print(f"Relay ON - Humidity ({humidity}%) is below threshold ({humidifier_on}%).")

            # Turn relay OFF if humidity is equal to or above humidifier_off threshold
            elif humidity >= humidifier_off:
                GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn relay OFF (lo-active)
                print(f"Relay OFF - Humidity ({humidity}%) is above threshold ({humidifier_off}%).")

            # Between thresholds, relay maintains its current state
            else:
                print(f"Humidity ({humidity}%) is within thresholds. Relay state unchanged.")

        else:
            print("Failed to get humidity data.")

    except Exception as e:
        print(f"Error in controlling relay: {e}")

def run_relay_control():
    """Continuously monitor the humidity and control relay based on thresholds."""
    try:
        while True:
            # Reload thresholds from the JSON file in each iteration
            humidifier_on, humidifier_off = load_thresholds_from_json()

            # Check and control the relay based on the latest thresholds
            check_and_control_relay(humidifier_on, humidifier_off)
            
            time.sleep(5)  # Check every 1 second

    except KeyboardInterrupt:
        print("Relay control stopped.")
    finally:
        GPIO.cleanup()  # Cleanup GPIO settings when done

if __name__ == "__main__":
    run_relay_control()
