import RPi.GPIO as GPIO
import time
#Dette script er bare en styring av GPIO18 ON/OFF (0V vs 3.3V)
#Ikke noe annet enn PRI boardet.
# Angi GPIO-nummeret du vil bruke
GPIO_PIN = 18

# Sett opp GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

try:
    while True:
        # Sett GPIO til høy (3.3V)
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        print("GPIO set to HIGH")
        time.sleep(1)  # Vent 1 sekund

        # Sett GPIO til lav (0V)
        GPIO.output(GPIO_PIN, GPIO.LOW)
        print("GPIO set to LOW")
        time.sleep(1)  # Vent 1 sekund

except KeyboardInterrupt:
    print("\nProgrammet avsluttet av brukeren.")
finally:
    # Rydd opp GPIO-innstillingene før programmet avsluttes
    GPIO.cleanup()
