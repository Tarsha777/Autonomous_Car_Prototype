import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import threading
from flask import Flask, render_template_string, Response

# ==== GPIO Setup ====
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

IN1, IN2 = 27, 17
IN3, IN4 = 23, 22
TRIG, ECHO = 5, 6

for pin in [IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# ==== Motor Control ====
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

# ==== Global Shared State ====
car_status = "Initializing..."
current_frame = None

# ==== Distance Measurement ====
def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.01)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start, pulse_end = 0, 0
    timeout = time.time() + 0.05
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return 100

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - pulse_start > 0.05:
            return 100

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

# ==== Traffic Light Detection ====
def detect_traffic_light(roi):
    blurred = cv2.GaussianBlur(roi, (5, 5), 0)
    B, G, R = cv2.split(blurred)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    red_diff = cv2.subtract(R, gray)
    green_diff = cv2.subtract(G, gray)

    _, red_thresh = cv2.threshold(red_diff, 50, 255, cv2.THRESH_BINARY)
    _, green_thresh = cv2.threshold(green_diff, 50, 255, cv2.THRESH_BINARY)

    red_area = np.sum(red_thresh == 255)
    green_area = np.sum(green_thresh == 255)

    if red_area >= 200:
        return "RED"
    elif green_area >= 100:
        return "GREEN"
    else:
        return "NONE"

# ==== Lane + Obstacle + Traffic Thread ====
def car_main():
    global current_frame, car_status
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (320, 240))
        roi = frame[160:240, :]
        traffic_roi = frame[0:100, :]
        current_frame = frame.copy()

        traffic_status = detect_traffic_light(traffic_roi)
        distance = get_distance()

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

        if traffic_status == "RED" or distance < 10:
            stop()
            reason = "RED LIGHT" if traffic_status == "RED" else "OBSTACLE"
            car_status = f"STOP ({reason})"
        elif left_m['m00'] > 5000 and right_m['m00'] > 5000:
            left_cx = int(left_m['m10'] / left_m['m00'])
            right_cx = int(right_m['m10'] / right_m['m00']) + width // 2
            cx = (left_cx + right_cx) // 2
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

            car_status = f"RUNNING ({direction})"
        else:
            stop()
            car_status = "STOP (NO LANE)"

    cap.release()
    GPIO.cleanup()
# ==== Flask Web Server (Updated) ====
app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Car Control Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 20px;
        }
        #videoFeed {
            width: 640px;
            height: 480px;
            border: 2px solid #333;
            margin-bottom: 20px;
        }
        .status-box {
            display: inline-block;
            padding: 10px 20px;
            margin: 0 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }
        .red { color: red; font-weight: bold; }
        .green { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Car Control Dashboard</h1>
    <img id="videoFeed" src="/video_feed">
   
    <div>
        <div class="status-box">
            <h3>Direction</h3>
            <p id="direction">--</p>
        </div>
        <div class="status-box">
            <h3>Traffic Light</h3>
            <p id="trafficLight">--</p>
        </div>
        <div class="status-box">
            <h3>Distance</h3>
            <p id="distance">-- cm</p>
        </div>
    </div>

    <script>
        function updateStatus() {
            fetch('/status')
                .then(response => {
                    if (!response.ok) throw new Error('Network error');
                    return response.json();
                })
                .then(data => {
                    document.getElementById('direction').textContent = data.direction || '--';
                   
                    const trafficElement = document.getElementById('trafficLight');
                    trafficElement.textContent = data.traffic_light || '--';
                    trafficElement.className = data.traffic_light === 'RED' ? 'red' : '';
                   
                    document.getElementById('distance').textContent =
                        (data.distance !== undefined ? data.distance + ' cm' : '-- cm');
                })
                .catch(error => console.log('Error:', error));
           
            setTimeout(updateStatus, 500);
        }
       
        // Start updating when page loads
        window.onload = updateStatus;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', current_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    # Get current traffic status from frame if available
    traffic_status = "NONE"
    distance = 0
    if current_frame is not None:
        try:
            traffic_roi = current_frame[0:100, :]
            traffic_status = detect_traffic_light(traffic_roi)
            distance = get_distance()
        except:
            pass
   
    return {
        'direction': car_status,
        'traffic_light': traffic_status,
        'distance': distance
    }

# ==== Main Entrypoint ====
if __name__ == '__main__':
    threading.Thread(target=car_main, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)