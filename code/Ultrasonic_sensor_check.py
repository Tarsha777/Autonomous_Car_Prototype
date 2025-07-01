import RPi.GPIO as GPIO
import time

# GPIO Mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Ultrasonic sensor(HC-SR04 Ultrasonic Sensor)
# Pins
TRIG = 5
ECHO = 6

# Setup
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    # Ensure TRIG is LOW
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    # Send 10µs HIGH pulse to TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for ECHO to go HIGH (start time)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Wait for ECHO to go LOW (end time)
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate duration
    pulse_duration = pulse_end - pulse_start

    # Calculate distance (speed of sound = 34300 cm/s)
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

# Test loop
try:
    while True:
        dist = measure_distance()
        print(f"Distance: {dist} cm")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopped by User")
    GPIO.cleanup()