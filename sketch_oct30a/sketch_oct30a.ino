#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

const char* ssid = "YOUR_SSID";          // Replace with your WiFi SSID
const char* password = "YOUR_PASSWORD";  // Replace with your WiFi Password
const char* serverName = "http://YOUR_LAPTOP_IP:5000/data";  // Replace with your laptop IP and port

const int sensor = A0;
const int flameSensorPin = A1;
int gas_value;

#define DHTPIN A2       // Pin connected to the DHT11
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  gas_value = analogRead(sensor);
  int flameValue = analogRead(flameSensorPin);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{\"temperature\":" + String(temperature) + ", \"humidity\":" + String(humidity) + ", \"gas_value\":" + String(gas_value) + ", \"flame_value\":" + String(flameValue) + "}";

    int httpResponseCode = http.POST(jsonData);
    if (httpResponseCode > 0) {
      Serial.print("Data sent, response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  delay(2000);
}
