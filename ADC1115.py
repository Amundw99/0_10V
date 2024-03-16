import smbus
import time

# Define ADC parameters
ADS1115_I2C_ADDR = 0x48  # I2C address of ADS1115 (default)
ADS1115_REG_POINTER_CONVERT = 0x00  # Conversion register
ADS1115_REG_CONFIG = 0x01  # Configuration register
ADS1115_REG_CONFIG_OS_SINGLE = 0x8000  # Single-shot conversion mode
ADS1115_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended A0 input
ADS1115_REG_CONFIG_PGA_6_144V = 0x0000  # +/-6.144V range (default)

# Create an instance of the smbus module
bus = smbus.SMBus(1)  # Raspberry Pi 3 uses I2C port 1

# Function to read a single analog pin value
def read_adc(channel):
    # Configuration for single-ended measurement on the specified channel
    config = (ADS1115_REG_CONFIG_OS_SINGLE |
              ADS1115_REG_CONFIG_MUX_SINGLE_0 |
              ADS1115_REG_CONFIG_PGA_6_144V |
              channel)
    # Write configuration data to ADS1115
    bus.write_i2c_block_data(ADS1115_I2C_ADDR, ADS1115_REG_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])
    # Wait for the conversion to complete (each conversion takes about 8 ms in single-shot mode)
    time.sleep(0.01)  # Increase if needed for stability
    # Read the converted data from ADS1115
    data = bus.read_i2c_block_data(ADS1115_I2C_ADDR, ADS1115_REG_POINTER_CONVERT, 2)
    # Convert the data to a single integer
    value = (data[0] << 8) | data[1]
    actual_voltage = value * (6.144 / 32768)
    return value, actual_voltage

try:
    while True:
        # Read the value from A0 pin
        adc_value, actual_voltage = read_adc(0)  # 0 represents A0 pin
        print("Analog value on A0 pin:", adc_value, "analog innspenning er ", round(actual_voltage,3))
        # Wait for one second before reading the value again
        time.sleep(0.3)

except KeyboardInterrupt:
    # Exit the program if Ctrl + C is pressed
    pass
