import RPi.GPIO as GPIO
import time

# Define GPIO pins connected to the relay inputs
RELAY_PINS = [20, 21, 26]  # Update with the GPIO pins you're using

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use Broadcom GPIO numbering
GPIO.setup(RELAY_PINS, GPIO.OUT, initial=GPIO.LOW)  # Set pins as outputs, initially OFF

def test_relays():
    try:
        print("Testing relays. Each will toggle on for 2 seconds...")
        for pin in RELAY_PINS:
            print(f"Activating relay on GPIO {pin}")
            GPIO.output(pin, GPIO.HIGH)  # Turn relay ON
            time.sleep(2)
            GPIO.output(pin, GPIO.LOW)   # Turn relay OFF
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        GPIO.cleanup()  # Ensure GPIO pins are reset
        print("GPIO cleanup done. Test complete.")

if __name__ == "__main__":
    test_relays()
