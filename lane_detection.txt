import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

IN1, IN2 = 27, 17
IN3, IN4 = 23, 22
for pin in [IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)

def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def left():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def right():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# Camera setup
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (320, 240))
    roi = frame[160:240, :]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 40, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)

    height, width = mask.shape
    left_mask = mask[:, :width//2]
    right_mask = mask[:, width//2:]

    left_m = cv2.moments(left_mask)
    right_m = cv2.moments(right_mask)

    direction = "STOP"
    cx = None

    if left_m['m00'] > 5000 and right_m['m00'] > 5000:
        left_cx = int(left_m['m10'] / left_m['m00'])
        right_cx = int(right_m['m10'] / right_m['m00']) + width // 2
        cx = (left_cx + right_cx) // 2

        cv2.circle(roi, (left_cx, 40), 5, (255, 0, 0), -1)
        cv2.circle(roi, (right_cx, 40), 5, (0, 0, 255), -1)
        cv2.circle(roi, (cx, 40), 5, (0, 255, 0), -1)

        deviation = cx - (width // 2)

        if deviation > 20:
            direction = "RIGHT"
            right()
        elif deviation < -20:
            direction = "LEFT"
            left()
        else:
            direction = "FORWARD"
            forward()
    else:
        direction = "STOP"
        stop()

    cv2.putText(roi, f'Direction: {direction}', (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.imshow("Dual Lane Tracker", roi)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        stop()
        break

cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()