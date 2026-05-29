import importlib
import sys
import types


def _reload_with_mocks(monkeypatch, humidity_value=None):
    # Create fake RPi.GPIO module
    fake_gpio = types.ModuleType('RPi.GPIO')
    fake_gpio.LOW = 0
    fake_gpio.HIGH = 1
    fake_gpio.BCM = 'BCM'
    state = {'last': fake_gpio.HIGH}

    def setmode(m):
        pass

    def setup(pin, mode, initial=None):
        if initial is not None:
            state['last'] = initial

    def output(pin, level):
        state['last'] = level

    def input(pin):
        return state['last']

    def cleanup():
        pass

    fake_gpio.setmode = setmode
    fake_gpio.setup = setup
    fake_gpio.output = output
    fake_gpio.input = input
    fake_gpio.cleanup = cleanup

    monkeypatch.setitem(sys.modules, 'RPi.GPIO', fake_gpio)

    # Provide a get_sensor_data mock module
    fake_get = types.ModuleType('get_sensor_data')

    def get_sensor_data_func():
        # returns (temperature, humidity)
        if humidity_value is None:
            return (25.0, 50.0)
        return (25.0, humidity_value)

    fake_get.get_sensor_data = get_sensor_data_func
    monkeypatch.setitem(sys.modules, 'get_sensor_data', fake_get)

    # Ensure fresh import
    if 'scripts.humidity_control' in sys.modules:
        del sys.modules['scripts.humidity_control']
    hc = importlib.import_module('scripts.humidity_control')
    return hc, fake_gpio


def test_write_relay_on_off(monkeypatch):
    hc, fake_gpio = _reload_with_mocks(monkeypatch)

    # Initially HIGH (OFF)
    assert fake_gpio.input(None) == fake_gpio.HIGH

    # Write ON -> should set LOW
    hc.write_relay('ON')
    assert fake_gpio.input(None) == fake_gpio.LOW
    assert hc.get_relay_state() == 1

    # Write OFF -> should set HIGH
    hc.write_relay('OFF')
    assert fake_gpio.input(None) == fake_gpio.HIGH
    assert hc.get_relay_state() == 0


def test_check_and_control_turns_on_and_off(monkeypatch):
    # Test turn ON when humidity below lower threshold
    hc, fake_gpio = _reload_with_mocks(monkeypatch, humidity_value=30.0)
    # Force config so lower threshold > humidity
    monkeypatch.setattr(hc, 'load_config', lambda: (50.0, 60.0, 1, 10, 'AUTO'))
    # Ensure last_relay_state starts HIGH
    hc.last_relay_state = fake_gpio.HIGH
    hc.check_and_control_relay()
    assert fake_gpio.input(None) == fake_gpio.LOW

    # Now test turn OFF when humidity above upper threshold
    # reload with high humidity
    hc, fake_gpio = _reload_with_mocks(monkeypatch, humidity_value=90.0)
    monkeypatch.setattr(hc, 'load_config', lambda: (50.0, 60.0, 1, 10, 'AUTO'))
    # Simulate relay currently ON (LOW)
    hc.last_relay_state = fake_gpio.LOW
    hc.check_and_control_relay()
    assert fake_gpio.input(None) == fake_gpio.HIGH


def test_sensor_failure_turns_off(monkeypatch):
    # Simulate sensor failure (humidity None)
    # Prepare mocks where get_sensor_data returns (None, None)
    fake_gpio = types.ModuleType('RPi.GPIO')
    fake_gpio.LOW = 0
    fake_gpio.HIGH = 1
    fake_gpio.BCM = 'BCM'
    state = {'last': fake_gpio.LOW}

    def setmode(m):
        pass

    def setup(pin, mode, initial=None):
        if initial is not None:
            state['last'] = initial

    def output(pin, level):
        state['last'] = level

    def input(pin):
        return state['last']

    def cleanup():
        pass

    fake_gpio.setmode = setmode
    fake_gpio.setup = setup
    fake_gpio.output = output
    fake_gpio.input = input
    fake_gpio.cleanup = cleanup

    monkeypatch.setitem(sys.modules, 'RPi.GPIO', fake_gpio)

    fake_get = types.ModuleType('get_sensor_data')
    fake_get.get_sensor_data = lambda: (None, None)
    monkeypatch.setitem(sys.modules, 'get_sensor_data', fake_get)

    if 'scripts.humidity_control' in sys.modules:
        del sys.modules['scripts.humidity_control']
    hc = importlib.import_module('scripts.humidity_control')

    # Set sensor_fail_limit to 1 via load_config
    monkeypatch.setattr(hc, 'load_config', lambda: (50.0, 60.0, 1, 1, 'AUTO'))
    hc.last_relay_state = fake_gpio.LOW
    hc.sensor_fail_count = 0
    hc.check_and_control_relay()
    # After failure, should have written OFF (HIGH)
    assert fake_gpio.input(None) == fake_gpio.HIGH
