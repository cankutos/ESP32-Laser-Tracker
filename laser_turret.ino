#include <WiFi.h>
#include <WiFiUdp.h>
#include <ESP32Servo.h>

// ==========================================
// ⚙️ WIFI SETTINGS
// ==========================================
const char* ssid = "YOUR_WIFI_SSID";       // Enter your WiFi name here
const char* password = "YOUR_WIFI_PASSWORD"; // Enter your WiFi password here

// ==========================================
// 🛠️ HARDWARE SETTINGS
// ==========================================
Servo panMotor;
Servo tiltMotor;

int panPin = 13;   // X-Axis (Left/Right)
int tiltPin = 14;  // Y-Axis (Up/Down)
int lazerPin = 32; // Laser Module Pin

WiFiUDP Udp;
unsigned int localPort = 4210;
char packetBuffer[255];

void setup() {
  Serial.begin(115200);

  // TURN ON THE LASER
  pinMode(lazerPin, OUTPUT);
  digitalWrite(lazerPin, HIGH);

  // Attach the servos
  panMotor.attach(panPin);
  tiltMotor.attach(tiltPin);

  // Startup Calibration Sequence (Test Movement)
  panMotor.write(0);
  tiltMotor.write(90);
  delay(500);
  panMotor.write(180);
  delay(500);
  panMotor.write(90); // Return to center

  // Connect to WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n✅ WiFi Connected!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // Start UDP Server
  Udp.begin(localPort);
  Serial.println("🎧 UDP Server listening on port 4210...");
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;
    
    String incomingData = String(packetBuffer);
    int commaIndex = incomingData.indexOf(',');
    
    if (commaIndex > 0) {
      // Parse the incoming UDP packet (Format: "panAngle,tiltAngle")
      int panAngle = incomingData.substring(0, commaIndex).toInt();
      int tiltAngle = incomingData.substring(commaIndex + 1).toInt();
      
      // Hardware Constraints to prevent physical damage
      if(panAngle < 0) panAngle = 0;
      if(panAngle > 180) panAngle = 180;
      if(tiltAngle < 40) tiltAngle = 40;
      if(tiltAngle > 140) tiltAngle = 140;

      // Execute movement
      panMotor.write(panAngle);
      tiltMotor.write(tiltAngle);
      
      // Debug Output
      Serial.print("🎯 Target Locked -> Pan: ");
      Serial.print(panAngle);
      Serial.print(" | Tilt: ");
      Serial.println(tiltAngle);
    }
  }
}
