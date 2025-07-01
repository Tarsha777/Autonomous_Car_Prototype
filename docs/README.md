# 🚗 Autonomous Car Prototype with Real-Time Web Dashboard

A smart self-driving car prototype combining **Lane Detection**, **Traffic Signal Recognition**, **Obstacle Avoidance**, and a **Real-Time Web Dashboard** for monitoring vehicle status and camera feed.

---

## 🛠️ Hardware Components

- Raspberry Pi 4 (64-bit OS Recommended)
- Ultrasonic Sensor (HC-SR04)
- USB Webcam
- Motor Driver (L298N or similar)
- DC Motors
- Car Chassis & Wheels
- Jumper Wires & Power Supply

---

## 💻 Software & Tech Stack

- **Python 3.13**
- **Flask** — Web Dashboard & Streaming
- **OpenCV** — Computer Vision (Lane & Traffic Light Detection)
- **Numpy** — Calculations & Processing
- **Imutils** — Image utilities (Optional)

### Install Dependencies


pip install -r requirements.txt


---

## ⚡ Key Features

✅ **Lane Detection** — Follows lane boundaries on black surface with white lines

✅ **Traffic Signal Recognition** — Stops at Red light, Moves on Green

✅ **Obstacle Avoidance** — Ultrasonic sensor prevents collisions (Stops if object < 20cm)

✅ **Real-Time Web Dashboard** —

 📷 Live camera feed
 
 📊 Car status (Obstacle distance, Traffic signal state)
 
 🌐 Accessible on browser within the same network
 

**Dashboard Access Example:**

http://<Your_Raspberry_Pi_IP>


*Example:* `http://192.168.1.5`

---

## 🚀 How to Run

1. Assemble hardware as per design
2. Connect Raspberry Pi to same network as your monitoring device
3. Run the main Python script
4. Open dashboard in your browser using Pi's IP

---

## 🎯 Known Limitations

⚠️ Lane detection optimized for controlled indoor track (Black chart with white lines)
⚠️ Basic color-based traffic light detection, sensitive to lighting conditions
⚠️ Obstacle detection range limited to 20cm with single ultrasonic sensor

---

## 🔥 Future Improvements

* AI-powered Object Detection (YOLO, MobileNet)
* Lane detection adaptable to real-world roads
* Multiple sensors for 360° awareness
* Advanced Web Dashboard with interactive controls

---

## 🎥 Demo Video

https://drive.google.com/file/d/1KMR6CaVmjxM7jrvvaXdzsDBnqUM_Cvvn/view?usp=sharing

---

## 📁 Project Structure

├── main.py               # Main control logic
├── lane_detection.py     # Lane following logic
├── traffic_light.py      # Traffic signal detection
├── obstacle_avoidance.py # Ultrasonic obstacle handling
├── dashboard/            # Web dashboard files (Flask app, HTML, CSS)
├── requirements.txt      # Python dependencies
└── README.md             # Project details

---

## 👨‍💻 Author

Developed by Tarsha Siva Teja Ponakala.

---


