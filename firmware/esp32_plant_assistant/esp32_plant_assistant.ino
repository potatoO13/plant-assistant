#include <WiFi.h>
#include <PubSubClient.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* MQTT_HOST = "YOUR_MQTT_HOST";
const int MQTT_PORT = 1883;

const char* DEVICE_ID = "device001";
const char* TELEMETRY_TOPIC = "plant/device001/telemetry";
const char* CONTROL_TOPIC = "plant/device001/control";
const char* CONTROL_ACK_TOPIC = "plant/device001/control_ack";

const int RELAY_PIN = 26;
const unsigned long TELEMETRY_INTERVAL_MS = 30000;
const int MAX_WATERING_SEC = 10;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

unsigned long lastTelemetryAt = 0;
bool watering = false;
unsigned long wateringStopAt = 0;
String currentRequestId = "";

struct SensorData {
  float temperature;
  float airHumidity;
  float soilMoisture;
  int light;
};

void connectWiFi();
void connectMQTT();
SensorData readSensors();
void publishTelemetry();
void handleControlCommand(char* topic, byte* payload, unsigned int length);
void startWatering(int durationSec, String requestId);
void stopWatering(String status);
void reconnect();

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  connectWiFi();
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setCallback(handleControlCommand);
  connectMQTT();
}

void loop() {
  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.loop();

  if (watering && millis() >= wateringStopAt) {
    stopWatering("done");
  }

  if (millis() - lastTelemetryAt >= TELEMETRY_INTERVAL_MS) {
    publishTelemetry();
    lastTelemetryAt = millis();
  }
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void connectMQTT() {
  while (!mqttClient.connected()) {
    if (mqttClient.connect("esp32-plant-assistant")) {
      mqttClient.subscribe(CONTROL_TOPIC);
      Serial.println("MQTT connected");
    } else {
      delay(2000);
    }
  }
}

SensorData readSensors() {
  SensorData data;

  // TODO: Replace with AHT20/DHT22 temperature and humidity reading.
  data.temperature = 23.0 + random(0, 50) / 10.0;
  data.airHumidity = 55.0 + random(0, 100) / 10.0;

  // TODO: Replace with soil moisture sensor analog reading and calibration.
  data.soilMoisture = 40.0 + random(0, 100) / 10.0;

  // TODO: Replace with BH1750 light sensor reading.
  data.light = 1000 + random(0, 800);

  return data;
}

void publishTelemetry() {
  SensorData data = readSensors();
  String payload = "{";
  payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  payload += "\"temperature\":" + String(data.temperature, 1) + ",";
  payload += "\"air_humidity\":" + String(data.airHumidity, 1) + ",";
  payload += "\"soil_moisture\":" + String(data.soilMoisture, 1) + ",";
  payload += "\"light\":" + String(data.light) + ",";
  payload += "\"timestamp\":\"";
  payload += "2026-05-08T20:30:00";
  payload += "\"}";

  mqttClient.publish(TELEMETRY_TOPIC, payload.c_str());
  Serial.println(payload);
}

void handleControlCommand(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  if (message.indexOf("\"command\":\"water\"") < 0) {
    return;
  }

  int durationSec = 5;
  int durationIndex = message.indexOf("\"duration_sec\":");
  if (durationIndex >= 0) {
    durationSec = message.substring(durationIndex + 15).toInt();
  }
  durationSec = constrain(durationSec, 1, MAX_WATERING_SEC);

  String requestId = "";
  int requestIndex = message.indexOf("\"request_id\":\"");
  if (requestIndex >= 0) {
    int start = requestIndex + 14;
    int end = message.indexOf("\"", start);
    requestId = message.substring(start, end);
  }

  startWatering(durationSec, requestId);
}

void startWatering(int durationSec, String requestId) {
  if (watering) {
    stopWatering("interrupted");
  }

  currentRequestId = requestId;
  watering = true;
  wateringStopAt = millis() + (unsigned long)durationSec * 1000UL;
  digitalWrite(RELAY_PIN, HIGH);
  Serial.println("Watering started");
}

void stopWatering(String status) {
  digitalWrite(RELAY_PIN, LOW);
  watering = false;

  String payload = "{";
  payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  payload += "\"request_id\":\"" + currentRequestId + "\",";
  payload += "\"command\":\"water\",";
  payload += "\"status\":\"" + status + "\",";
  payload += "\"timestamp\":\"2026-05-08T20:30:00\"";
  payload += "}";

  mqttClient.publish(CONTROL_ACK_TOPIC, payload.c_str());
  Serial.println("Watering stopped");
}

void reconnect() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  connectMQTT();
}
