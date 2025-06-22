// Arduino LSM6DS3 - Accelerometer & Gyrpscope
  
#include <Arduino_LSM6DS3.h>
#include <ArduinoJson.h>

//create JSON document
StaticJsonDocument<200> doc; // allocates 200 bytes for JSON (could reduce?)

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
  float x, y, z;

  // ACCELEROMETER
  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
    IMU.readAcceleration(x, y, z);
  
    // save values to json object
    doc["Ax"] = x;
    doc["Ay"] = y;
    doc["Az"] = z;

    IMU.readGyroscope(x, y, z);
  
    // save values to json object
    doc["Gx"] = x;
    doc["Gy"] = y;
    doc["Gz"] = z;

    serializeJson(doc, Serial);
    Serial.print('\n');
  }  
}
