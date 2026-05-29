# Handles logic for automatic humidifier control based on humidity thresholds and safety settings.

import RPi.GPIO as GPIO
import time
import sys
import os
import json
import threading
import logging
from logging.handlers import RotatingFileHandler


# Add the 'scripts' folder to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Import get_sensor_data
import get_sensor_data  # Now using the get_sensor_data module to fetch sensor data

# Constants
RELAY_PIN = 20  # GPIO pin for Relay 2 (connected to pin 38)
THRESHOLD_FILE = os.path.join(os.path.dirname(__file__), '../variables/variables.json')  # Path to JSON file

# Initialize GPIO settings
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Default relay state OFF

# Global state variables
last_relay_state = GPIO.HIGH  # Stores last known relay state
relay_state_lock = threading.Lock() # Lock for thread-safe relay state access
current_humidifier_state = GPIO.HIGH  # Default OFF
last_switch_time = 0  # Timestamp of last relay switch
sensor_fail_count = 0  # Tracks consecutive sensor failures

# Stop flag for graceful shutdown
stop_flag = False

# Configure structured file logger
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'humidity_control.log')
logger = logging.getLogger('humidity_control')
if not logger.handlers:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    # JSON-like single-line formatter
    fmt = '{"ts":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","message":"%(message)s"}'
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def load_config():
    """
    Load humidity thresholds, debounce delay, and sensor fail limit from JSON.
    Returns (lower_threshold, upper_threshold, debounce_delay, sensor_fail_limit).
    """
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


def write_relay(requested_logical_state):
    """Write the relay GPIO with logging.

    Logs:
    1) what the program requested (logical ON/OFF)
    2) that the GPIO.output was called (physical level written)
    3) the GPIO.input read-back value (physical level read)

    Returns the read-back GPIO value (GPIO.HIGH or GPIO.LOW) or None on error.
    """
    global last_relay_state, current_humidifier_state

    # Map logical state to physical GPIO level (relay is active-low)
    level = GPIO.LOW if requested_logical_state == 'ON' else GPIO.HIGH

    try:
        logger.info(f"relay_request: requested={requested_logical_state} level={level}")
        GPIO.output(RELAY_PIN, level)
        logger.info(f"gpio_write: written_level={level}")
    except Exception as e:
        logger.error(f"error_writing_gpio: {e}")

    # Read back actual GPIO level
    try:
        actual = GPIO.input(RELAY_PIN)
        logger.info(f"gpio_readback: read_level={actual}")
    except Exception as e:
        actual = None
        logger.error(f"error_reading_gpio: {e}")

    # Update internal state using the read-back value when available
    with relay_state_lock:
        if actual is not None:
            last_relay_state = actual
            # Maintain the convention: current_humidifier_state uses GPIO.LOW for ON
            current_humidifier_state = GPIO.LOW if actual == GPIO.LOW else GPIO.HIGH
        else:
            # Fallback to requested level if read-back failed
            last_relay_state = level
            current_humidifier_state = GPIO.LOW if level == GPIO.LOW else GPIO.HIGH

    return actual

def check_and_control_relay():
    global last_relay_state, last_switch_time, sensor_fail_count, current_humidifier_state

    lower_threshold, upper_threshold, debounce_delay, sensor_fail_limit, mode = load_config()

    if mode == "ON":
        write_relay('ON')
        print("Mode ON: Forcing relay ON")
        return
    elif mode == "OFF":
        write_relay('OFF')
        print("Mode OFF: Forcing relay OFF")
        return

    # If mode is AUTO, proceed with normal logic...
    try:
        temperature, humidity = get_sensor_data.get_sensor_data()  # Fetch sensor data

        if humidity is None:
            sensor_fail_count += 1
            logger.warning(f"sensor_read_failed: count={sensor_fail_count} limit={sensor_fail_limit}")
            
            # If sensor keeps failing, turn relay OFF for safety
            if sensor_fail_count >= sensor_fail_limit:
                if last_relay_state == GPIO.LOW:
                    write_relay('OFF')
                    logger.info("sensor_failure_action: relay_off_for_safety")
            return  # Skip further processing on failure
        
        # Reset sensor failure count on successful read
        sensor_fail_count = 0
        logger.info(f"sensor_read: humidity={humidity}")

        # Get current time
        current_time = time.time()

        logger.debug(f"relay_debug: last_relay_state={last_relay_state} last_switch_time={last_switch_time} current_time={current_time}")

        # Check if relay needs to switch ON
        if humidity < lower_threshold and last_relay_state == GPIO.HIGH:
                if current_time - last_switch_time >= debounce_delay:
                    logger.info("action: turning_relay_on")
                    write_relay('ON')
                    last_switch_time = current_time
                    logger.info("state_change: relay_on_humidity_below_lower")

        # Check if relay needs to switch OFF
        elif humidity > upper_threshold and last_relay_state == GPIO.LOW:
            if current_time - last_switch_time >= debounce_delay:
                logger.info("action: turning_relay_off")
                write_relay('OFF')
                last_switch_time = current_time
                logger.info("state_change: relay_off_humidity_above_upper")

        # Maintain current relay state if within thresholds
        else:
            logger.debug("relay_no_change: humidity_within_thresholds")

    except Exception as e:
        logger.error(f"error_relay_control_logic: {e}")

def initialize_relay_state():
    """
    Reads initial humidity and sets the correct relay state on startup.
    """
    global last_relay_state

    lower_threshold, upper_threshold, _, _, _ = load_config()
    _, humidity = get_sensor_data.get_sensor_data()

    if humidity is not None:
        if humidity < lower_threshold:
            write_relay('ON')
            logger.info("startup: relay_on_humidity_below_lower")
        elif humidity > upper_threshold:
            write_relay('OFF')
            logger.info("startup: relay_off_humidity_above_upper")
        else:
            logger.info("startup: humidity_within_range_no_change")
    else:
        logger.warning("startup: sensor_read_failed_defaulting_relay_off")
        write_relay('OFF')  # Fail-safe default

def run_relay_control():
    """Continuously monitor humidity and control relay based on thresholds."""
    global stop_flag
    initialize_relay_state()  # Ensure correct startup state

    try:
        while not stop_flag:  # Check the stop flag
            check_and_control_relay()
            time.sleep(3)  # Check every 3 seconds (adjustable)
    except KeyboardInterrupt:
        logger.info("relay_control_stopped_keyboard_interrupt")
    except Exception as e:
        logger.error(f"error_humidity_control_thread: {e}")
    finally:
        logger.info("cleaning_up_gpio_in_humidity_control")
        GPIO.cleanup()

def stop_relay_control():
    """Signal the relay control loop to stop."""
    global stop_flag
    stop_flag = True
    print("Stopping humidity control thread...")

# This function is used to get the current relay state to write to the database
def get_relay_state():
    try:
        actual = GPIO.input(RELAY_PIN)
        logger.info(f"get_relay_state: gpio_input={actual}")
        return 1 if actual == GPIO.LOW else 0
    except Exception as e:
        logger.error(f"error_reading_relay_state_in_get_relay_state: {e}")
        with relay_state_lock:
            return 1 if current_humidifier_state == GPIO.LOW else 0

if __name__ == "__main__":
    run_relay_control()