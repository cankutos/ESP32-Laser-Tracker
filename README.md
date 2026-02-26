# 🎯 WiFi-Controlled Pan-Tilt Laser Turret

## 📌 Project Overview
This project is an ESP32-based 2-axis (Pan-Tilt) motion control system equipped with a laser module. It utilizes **UDP communication** over Wi-Fi to receive real-time coordinate data (`panAngle, tiltAngle`) and instantly drives the servo motors to target the specific location. 

This mechanism serves as the foundational hardware for advanced mechatronic applications, such as autonomous computer-vision object tracking and automated targeting systems.

## 🚀 Key Features
* **2-Axis Synchronization:** Seamless control of both X (Pan) and Y (Tilt) axes using two independent servo motors.
* **Low-Latency Communication:** Utilizes the UDP protocol over a local Wi-Fi network for rapid, real-time angle updates without the overhead of TCP.
* **Hardware Protection:** Implemented software-level angle constraints (e.g., Tilt bounded between 40° and 140°) to prevent physical strain or damage to the servo mechanisms.
* **Auto-Calibration:** Features a startup sequence to test motor limits and return the turret to a dead-center default position.

## 🛠️ Hardware Components
* ESP32 Development Board
* 2x SG90 Micro Servo Motors (Pan & Tilt mechanism)
* 5V Laser Diode Module
* Custom/3D-Printed Pan-Tilt Bracket
* Jumper wires & external power supply (for servos)

## ⚙️ How It Works
1. The ESP32 connects to the designated Wi-Fi network and starts a UDP server on port `4210`.
2. A client (e.g., a Python script processing camera feeds) sends a string packet in the format of `"panAngle,tiltAngle"` (e.g., `"90,120"`).
3. The ESP32 parses the string, applies boundary constraints, and executes the movement via the `ESP32Servo` library.
4. The laser points precisely to the commanded coordinate.

## 📄 License
This project is licensed under the MIT License.
