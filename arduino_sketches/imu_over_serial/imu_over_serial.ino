// Arduino LSM6DS3 - Accelerometer & Gyrpscope

#include <Arduino_LSM6DS3.h>
#include <ArduinoJson.h>

//create JSON document
StaticJsonDocument<200> doc; // allocates 200 bytes for JSON (could reduce?)

const unsigned long interval = 10; // 10ms for 100Hz
unsigned long lastUpdate = 0;
bool useRefreshRate = true; // use refresh rate if available

void setup() {
  // Setup up serial monitor
  Serial.begin(9600);
  while (!Serial);

  // check that IMU is connected & working
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
}

void loop() {
  unsigned long now = millis();
  if (now - lastUpdate < interval && useRefreshRate) return;
  lastUpdate = now;

  float x, y, z;

  // ACCELEROMETER
  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
    IMU.readAcceleration(x, y, z);

    // save values to json object
    // Convert acceleration from g to m/s^2 (1g = 9.80665 m/s^2)
    doc["Ax"] = x * 9.80665;
    doc["Ay"] = y * 9.80665;
    doc["Az"] = z * 9.80665;

    IMU.readGyroscope(x, y, z);

    // save values to json object
    // Convert gyroscope from dps (degrees per second) to rad/s (radians per second)
    doc["Gx"] = x * DEG_TO_RAD;
    doc["Gy"] = y * DEG_TO_RAD;
    doc["Gz"] = z * DEG_TO_RAD;

    serializeJson(doc, Serial);
    Serial.print('\n');
  }
}
