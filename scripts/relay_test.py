import unittest
from unittest.mock import patch, MagicMock
import humidity_control

class TestHumidityControl(unittest.TestCase):
    @patch('humidity_control.GPIO')
    @patch('humidity_control.get_sensor_data')
    @patch('humidity_control.time')
    def test_relay_control_logic(self, mock_time, mock_get_sensor_data, mock_gpio):
        """
        Test the relay control logic under different humidity conditions.
        """
        # Mock GPIO setup
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        mock_gpio.input.return_value = mock_gpio.HIGH  # Default relay state is OFF

        # Mock load_config to return test thresholds and debounce delay
        humidity_control.load_config = MagicMock(return_value=(85.0, 88.22, 15, 10))

        # Mock time.time() to simulate passage of time
        mock_time.time.return_value = 1000  # Simulate a fixed time

        # Test case 1: Humidity below lower threshold (relay should turn ON)
        mock_get_sensor_data.get_sensor_data.return_value = (25.0, 80.0)  # (temperature, humidity)
        humidity_control.check_and_control_relay()
        mock_gpio.output.assert_called_with(humidity_control.RELAY_PIN, mock_gpio.LOW)
        print("Test 1 Passed: Relay turned ON when humidity < lower threshold.")

        # Test case 2: Humidity above upper threshold (relay should turn OFF)
        mock_get_sensor_data.get_sensor_data.return_value = (25.0, 90.0)  # (temperature, humidity)
        humidity_control.check_and_control_relay()
        mock_gpio.output.assert_called_with(humidity_control.RELAY_PIN, mock_gpio.HIGH)
        print("Test 2 Passed: Relay turned OFF when humidity > upper threshold.")

    @patch('humidity_control.GPIO')
    @patch('humidity_control.get_sensor_data')
    def test_initialize_relay_state(self, mock_get_sensor_data, mock_gpio):
        """
        Test the initialization of the relay state on startup.
        """
        # Mock GPIO setup
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0

        # Mock load_config to return test thresholds
        humidity_control.load_config = MagicMock(return_value=(85.0, 88.22, 15, 10))

        # Test case 1: Humidity below lower threshold (relay should turn ON)
        mock_get_sensor_data.get_sensor_data.return_value = (25.0, 80.0)  # (temperature, humidity)
        humidity_control.initialize_relay_state()
        mock_gpio.output.assert_called_with(humidity_control.RELAY_PIN, mock_gpio.LOW)
        print("Test 3 Passed: Relay initialized to ON when humidity < lower threshold.")

        # Test case 2: Humidity above upper threshold (relay should turn OFF)
        mock_get_sensor_data.get_sensor_data.return_value = (25.0, 90.0)  # (temperature, humidity)
        humidity_control.initialize_relay_state()
        mock_gpio.output.assert_called_with(humidity_control.RELAY_PIN, mock_gpio.HIGH)
        print("Test 4 Passed: Relay initialized to OFF when humidity > upper threshold.")

if __name__ == "__main__":
    unittest.main()