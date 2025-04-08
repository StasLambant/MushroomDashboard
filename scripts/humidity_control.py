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
THRESHOLD_FILE = os.path.join(os.path.dirname(__file__), '../variables/variables.json')  # Path to JSON file

# Initialize GPIO settings
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Default relay state OFF

# Global state variables
last_relay_state = GPIO.HIGH  # Stores last known relay state
last_switch_time = 0  # Timestamp of last relay switch
sensor_fail_count = 0  # Tracks consecutive sensor failures

# Stop flag for graceful shutdown
stop_flag = False

def load_config():
    """
    Load humidity thresholds, debounce delay, and sensor fail limit from JSON.
    Returns (lower_threshold, upper_threshold, debounce_delay, sensor_fail_limit).
    """
def load_config():
    try:
        with open(THRESHOLD_FILE, 'r') as file:
            data = json.load(file)
            return (
                data.get("lower", 85.00),
                data.get("upper", 88.22),
                data.get("debounce_delay", 15),
                data.get("sensor_fail_limit", 10),
                data.get("mode", "AUTO")
            )
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return 85.00, 88.22, 15, 10, "AUTO"


def check_and_control_relay(): #manual mode
    global last_relay_state, last_switch_time, sensor_fail_count

    lower_threshold, upper_threshold, debounce_delay, sensor_fail_limit, mode = load_config()

    if mode == "ON":
        GPIO.output(RELAY_PIN, GPIO.LOW)
        last_relay_state = GPIO.LOW
        print("Mode ON: Forcing relay ON")
        return
    elif mode == "OFF":
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        last_relay_state = GPIO.HIGH
        print("Mode OFF: Forcing relay OFF")
        return

    # If mode is AUTO, proceed with normal logic...

    try:
        temperature, humidity = get_sensor_data.get_sensor_data()  # Fetch sensor data

        if humidity is None:
            sensor_fail_count += 1
            print(f"Sensor read failed ({sensor_fail_count}/{sensor_fail_limit})")
            
            # If sensor keeps failing, turn relay OFF for safety
            if sensor_fail_count >= sensor_fail_limit:
                if last_relay_state == GPIO.LOW:
                    GPIO.output(RELAY_PIN, GPIO.HIGH)
                    last_relay_state = GPIO.HIGH
                    print("Sensor failure: Turning relay OFF for safety.")
            return  # Skip further processing on failure
        
        # Reset sensor failure count on successful read
        sensor_fail_count = 0
        print(f"Current Humidity: {humidity}%")

        # Get current time
        current_time = time.time()

        print(f"last_relay_state: {last_relay_state}, last_switch_time: {last_switch_time}, current_time: {current_time}")

        # Check if relay needs to switch ON
        if humidity < lower_threshold and last_relay_state == GPIO.HIGH:
            if current_time - last_switch_time >= debounce_delay:
                print("Turning relay ON")
                GPIO.output(RELAY_PIN, GPIO.LOW)
                last_relay_state = GPIO.LOW
                last_switch_time = current_time
                print("Relay ON - Humidity below lower threshold.")

        # Check if relay needs to switch OFF
        elif humidity > upper_threshold and last_relay_state == GPIO.LOW:
            if current_time - last_switch_time >= debounce_delay:
                print("Turning relay OFF")
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                last_relay_state = GPIO.HIGH
                last_switch_time = current_time
                print("Relay OFF - Humidity above upper threshold.")

        # Maintain current relay state if within thresholds
        else:
            print("Relay state unchanged.") 

    except Exception as e:
        print(f"Error in relay control logic: {e}")

def initialize_relay_state():
    """
    Reads initial humidity and sets the correct relay state on startup.
    """
    global last_relay_state

    lower_threshold, upper_threshold, _, _, _ = load_config()
    _, humidity = get_sensor_data.get_sensor_data()

    if humidity is not None:
        if humidity < lower_threshold:
            GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn ON relay
            last_relay_state = GPIO.LOW
            print("Startup: Relay ON (Humidity below lower threshold).")
        elif humidity > upper_threshold:
            GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn OFF relay
            last_relay_state = GPIO.HIGH
            print("Startup: Relay OFF (Humidity above upper threshold).")
        else:
            print("Startup: Humidity within set range, relay state unchanged.")
    else:
        print("Startup: Sensor read failed, defaulting relay to OFF for safety.")
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Fail-safe default

def run_relay_control():
    """Continuously monitor humidity and control relay based on thresholds."""
    global stop_flag
    initialize_relay_state()  # Ensure correct startup state

    try:
        while not stop_flag:  # Check the stop flag
            check_and_control_relay()
            time.sleep(3)  # Check every 3 seconds (adjustable)
    except KeyboardInterrupt:
        print("Relay control stopped.")
    except Exception as e:
        print(f"Error in humidity control thread: {e}")
    finally:
        print("Cleaning up GPIO in humidity control...")
        GPIO.cleanup()

def stop_relay_control():
    """Signal the relay control loop to stop."""
    global stop_flag
    stop_flag = True
    print("Stopping humidity control thread...")

if __name__ == "__main__":
    run_relay_control()