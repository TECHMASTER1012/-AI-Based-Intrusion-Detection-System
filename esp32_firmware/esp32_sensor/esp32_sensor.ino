/*
 * ESP32-N16R8 IoT Device Node Firmware
 * Smart Intrusion Detection System - Network Fingerprinting Baseline
 * 
 * Target Server IP: http://10.62.241.135:5000/api/telemetry
 */

#include <WiFi.h>
#include <HTTPClient.h>

// ================= USER CONFIGURATION =================
const char* ssid     = "POCO X5 5G";      // Replace with your Wi-Fi name
const char* password = "Radhe Radhe";  // Replace with your Wi-Fi password

// Your Computer 1 (IDS Server) LAN IP Address
const char* serverUrl = "http://10.62.241.123:5000/api/telemetry";

// Telemetry interval (3 seconds)
const unsigned long interval = 3000;
unsigned long lastSendTime = 0;
// ======================================================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n[ESP32-N16R8] Initializing IoT Node...");
  Serial.print("[ESP32-N16R8] Connecting to Wi-Fi SSID: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n[ESP32-N16R8] Connected to Wi-Fi!");
  Serial.print("[ESP32-N16R8] Assigned Device IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - lastSendTime >= interval) {
    lastSendTime = currentMillis;
    
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");
      
      // Simulate IoT environmental telemetry
      float temp = 22.0 + (random(-20, 50) / 10.0);
      float humidity = 55.0 + (random(-50, 50) / 10.0);
      
      String payload = "{\"device_id\":\"ESP32_N16R8_Node\",\"temp\":" + String(temp, 1) + ",\"humidity\":" + String(humidity, 1) + "}";
      
      Serial.print("[ESP32-N16R8] Sending Telemetry: ");
      Serial.println(payload);
      
      int httpCode = http.POST(payload);
      
      if (httpCode > 0) {
        Serial.printf("[ESP32-N16R8] Server Response Code: %d\n", httpCode);
      } else {
        Serial.printf("[ESP32-N16R8] HTTP POST failed, error: %s\n", http.errorToString(httpCode).c_str());
      }
      
      http.end();
    } else {
      Serial.println("[ESP32-N16R8] Wi-Fi connection lost, attempting reconnect...");
      WiFi.reconnect();
    }
  }
}
