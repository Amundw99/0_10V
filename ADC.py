import smbus
import time

# Define ADC parameters
ADS1015_I2C_ADDR = 0x48  # I2C address of ADS1015
ADS1015_REG_POINTER_CONVERT = 0x00  # Conversion register
ADS1015_REG_CONFIG = 0x01  # Configuration register
ADS1015_REG_CONFIG_OS_SINGLE = 0x8000  # Single-shot conversion mode
ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended A0 input


# Create an instance of the smbus module
bus = smbus.SMBus(1)  # Raspberry Pi 3 bruker I2C-port 1

# Function to read a single analog pin value
def read_adc(channel):
    # Configuration for single-ended measurement on the specified channel
    config = ADS1015_REG_CONFIG_OS_SINGLE | ADS1015_REG_CONFIG_MUX_SINGLE_0 | channel
    # Write configuration data to ADS1015
    bus.write_i2c_block_data(ADS1015_I2C_ADDR, ADS1015_REG_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])
    # Wait for the conversion to complete (each conversion takes about 1 ms)
    time.sleep(0.1)
    # Read the converted data from ADS1015
    data = bus.read_i2c_block_data(ADS1015_I2C_ADDR, ADS1015_REG_POINTER_CONVERT, 2)
    print("data:", data)
    # Check if data is empty
    if len(data) < 2:
        return None
    # Convert the data to a single integer
    value = (data[0] << 8) | data[1]
    return value


try:
    while True:
        # Read the value from A0 pin
        adc_value = read_adc(3)  # 0 represents A0 pin
        if adc_value is not None:
            print("Analog value on A0 pin:", adc_value)
        else:
            print("Failed to read ADC value")
        # Wait for one second before reading the value again
        time.sleep(1)

except KeyboardInterrupt:
    # Exit the program if Ctrl + C is pressed
    pass