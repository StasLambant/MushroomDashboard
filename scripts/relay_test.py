import RPi.GPIO as GPIO
import time

# Constants
RELAY_PIN = 26  # GPIO pin for Relay 1 (connected to pin 37)

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Start with relay OFF (lo-active)

try:
    # Turn the relay ON (lo-active)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Relay is ON. Press Ctrl+C to exit.")

    # Keep the script running
    while True:
        time.sleep(3)  # Sleep to prevent busy-waiting

except KeyboardInterrupt:
    print("\nExiting and cleaning up GPIO...")

finally:
    # Cleanup GPIO settings
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn relay OFF
    GPIO.cleanup()
    print("GPIO cleaned up. Relay is OFF.")
