# Read A0, A1 and A2 sequensial ADS1115.
# Status: OK, working good
# Tip: Important to understand Config register Figure 36 on page 28 in texas Datasheet

import smbus
import time
import paho.mqtt.client as mqtt
import json
from _datetime import datetime
import pytz

broker_hostname = "farmer.cloudmqtt.com"
broker_port = 12212
broker_topic = "mrfdatarsp"

# Callback-funksjoner som definert tidligere
def on_connect(client, userdata, flags, rc):
    print("Tilkoblet med resultatkode " + str(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Uventet disconnection.")

def on_publish(client, userdata, mid):
    print("Melding publisert.")

# Opprett og konfigurer MQTT-klienten
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish


# Koble til MQTT-broker
client.username_pw_set("tyxnupyb", "jnuadovfo3_c")
client.connect(broker_hostname, broker_port, 60)

# Start nettverksslyngen i en separat tråd
client.loop_start()


# Define ADC parameters
ADS1115_I2C_ADDR = 0x48  # I2C address of ADS1115 (default) OK
ADS1115_REG_POINTER_CONVERT = 0x00  # Conversion register  OK
ADS1115_REG_CONFIG = 0x01  # Configuration register
ADS1115_REG_CONFIG_OS_SINGLE = 0x8000  # Single-shot conversion mode
ADS1115_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended A0 input
ADS1115_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended A1 input
ADS1115_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended A2 input
ADS1115_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended A3 input
ADS1115_REG_CONFIG_PGA_4_096V = 0x0200  # +/-4.096 range (default) # config register xxxx 0010 xxxx xxxx which means 0x02

# Create an instance of the smbus module
bus = smbus.SMBus(1)  # Raspberry Pi uses I2C port 1

# Function to read a single analog pin value
def read_adc(channel):
    # Select the correct MUX configuration for the channel
    if channel == 0:
        config_mux = ADS1115_REG_CONFIG_MUX_SINGLE_0
    elif channel == 1:
        config_mux = ADS1115_REG_CONFIG_MUX_SINGLE_1
    elif channel == 2:
        config_mux = ADS1115_REG_CONFIG_MUX_SINGLE_2
    elif channel == 3:
        config_mux = ADS1115_REG_CONFIG_MUX_SINGLE_3
    else:
        return 0  # Invalid channel

    config = (ADS1115_REG_CONFIG_OS_SINGLE |
              config_mux |
              ADS1115_REG_CONFIG_PGA_4_096V)
    # Write configuration data to ADS1115
    bus.write_i2c_block_data(ADS1115_I2C_ADDR, ADS1115_REG_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])
    # Wait for the conversion to complete
    time.sleep(0.4)  # Increase if needed for stability. If to fast, wrong values on ports will occur. Limit around 0.2 sec in this code
    # Read the converted data from ADS1115
    data = bus.read_i2c_block_data(ADS1115_I2C_ADDR, ADS1115_REG_POINTER_CONVERT, 2)
    # Convert the data to a single integer
    value = (data[0] << 8) | data[1]
    actual_voltage = value * (4.096 / 32768)  # Total range 65535, but use 32768 since only positive values
    return value, actual_voltage

try:
    while True:
        # Read the value from A0 pin
        adc_value_A0, actual_voltage_A0 = read_adc(0)  # 0 represents A0 pin
        time.sleep(2)
        adc_value_A1, actual_voltage_A1 = read_adc(1)  # 0 represents A1 pin
        time.sleep(2)
        adc_value_A2, actual_voltage_A2 = read_adc(2)  # 0 represents A0 pin
        time.sleep(2)
        current_datetime = datetime.now()
        measure_time = current_datetime.strftime("%d.%m.%Y %H.%M.%S")
        ts=datetime.timestamp(current_datetime)
        print("Analog A0 pin:", adc_value_A0, "Analog A0 volt:", round(actual_voltage_A0, 2), "Analog A1 pin:",
              adc_value_A1,
              "Analog A1 volt:", round(actual_voltage_A1, 2), "Analog A2 pin:", adc_value_A2, "Analog A2 volt:",
              round(actual_voltage_A2, 2))
        print("Radon A0 pin:", round(actual_voltage_A0*400/3.333, 2), "Analog A0 volt:", round(actual_voltage_A0, 2), "Radon A1 pin:",
              round(actual_voltage_A1*400/3.333, 2),
              "Analog A1 volt:", round(actual_voltage_A1, 2), "Radon A2 pin:", round(actual_voltage_A2*400/3.333, 2), "Analog A2 volt:",
              round(actual_voltage_A2, 2))

        #overfører A0,A1 og A2 som radonverdier
        data = {"owner": "MM",
                "dateTime":measure_time,
                "tid": str(ts),
                'A0': round(actual_voltage_A0*400/3.333, 0),  # Erstatt med din faktiske verdi for A0 og max 2 desialer
                'A1': round(actual_voltage_A1*400/3.333, 0),  # Erstatt med din faktiske verdi for A1
                'A2': round(actual_voltage_A2*400/3.333, 0)  # Erstatt med din faktiske verdi for A2
            }
        # Konvertere data til JSON-format
        json_data = json.dumps(data)

        # Publisere JSON-data til MQTT-topic
        client.publish(broker_topic, json_data)
        # Wait for one second before reading the value again
        time.sleep(42)


except KeyboardInterrupt:
    # Exit the program if Ctrl + C is pressed
    client.loop_stop()
    client.disconnect()
    pass
