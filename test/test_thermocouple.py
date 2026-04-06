import time
import spidev

# Open SPI bus 0, device 0 (CE0)
spi = spidev.SpiDev()
spi.open(0, 0)   # bus 0, CE0
spi.max_speed_hz = 5000000
spi.mode = 0

def read_max31855():
    # Read 4 bytes from the MAX31855
    raw = spi.xfer2([0x00, 0x00, 0x00, 0x00])
    value = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]

    # Check for fault
    if value & 0x7:
        # Bit 2: SCV, bit 1: SCG, bit 0: OC
        print("Thermocouple fault, status bits:", value & 0x7)
        return None, None

    # Thermocouple temperature (bits 31..18, signed, 0.25°C units)
    tc_raw = value >> 18  # shift down so bit 13 is sign bit
    if tc_raw & 0x2000:   # sign bit set?
        tc_raw -= 0x4000  # sign-extend negative value
    tc_temp_c = tc_raw * 0.25

    # Internal (cold junction) temperature (bits 15..4, signed, 0.0625°C units)
    cj_raw = (value >> 4) & 0xFFF
    if cj_raw & 0x800:
        cj_raw -= 0x1000
    cj_temp_c = cj_raw * 0.0625

    return tc_temp_c, cj_temp_c

try:
    while True:
        try:
            tc, cj = read_max31855()
            if tc is not None:
                print(f"Thermocouple: {tc:.2f} °C, Cold junction: {cj:.2f} °C")
            else:
                print("Read error / fault from MAX31855")
        except Exception as e:
            print("Error:", e)

        time.sleep(1)
finally:
    spi.close()
