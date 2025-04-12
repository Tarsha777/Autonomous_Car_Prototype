import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define GPIO pins
TRIG = 25
ECHO = 24
SERVO = 5
# Pin Definitions
IN1 = 17  # IN1 connected to GPIO 17
IN2 = 27  # IN2 connected to GPIO 27
IN3 = 22  # IN3 connected to GPIO 22
IN4 = 23  # IN4 connected to GPIO 23

# Set GPIO pins as output and input
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO, GPIO.OUT)

# Initialize the servo motor
servo = GPIO.PWM(SERVO, 50)  # 50 Hz frequency for servo
servo.start(7.5)  # Servo in neutral position (facing forward)

def distance():
    # Send trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for the echo
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate the distance
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Convert time to distance (in cm)
    distance = round(distance, 2)
    print(distance)
    return distance

def check_obstacle():
    dist = distance()
    print(f"Distance to obstacle: {dist} cm")
    return dist < 70  # If an obstacle is within 30 cm, trigger avoidance

def rotate_servo(angle):
    # Convert angle to duty cycle
    duty = (angle / 18) + 2.5
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)

# GPIO Setup
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

def backward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN4, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
   

def forward():
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def left():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def right():
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN4, GPIO.HIGH)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
def stop():
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
c=0

try:
    while True:
        if not check_obstacle():
            forward()
        # Check if there's an obstacle in front
        elif check_obstacle():
            c+=1
            backward()
            time.sleep(0.5)
            stop()
            time.sleep(0.5)
            print("Obstacle detected! Checking left and right...")
           
            # Check to the left (90° to the left)
            rotate_servo(45)  # Left
            left_distance = distance()
            print(f"Distance to the left: {left_distance} cm")
           
            # Check to the right (90° to the right)
            rotate_servo(135)  # Right
            right_distance = distance()
            print(f"Distance to the right: {right_distance} cm")

            # Return to the forward position
            rotate_servo(90)  # Forward

            # Choose the path with the most clearance
            if left_distance < right_distance:
                c=0
                left()
                time.sleep(0.1)
                print("Turning left...")
                # Add code here to turn left (e.g., control motors)
            elif left_distance>right_distance:
                c=0
                right()
                time.sleep(0.1)
                print("Turning right...")
                # Add code here to turn right (e.g., control motors)
            elif c==3:
                backward()
                time.sleep(1)
               
       
        time.sleep(1)
 


finally:
    # Clean up the GPIO settings
    GPIO.cleanup()