#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#define LDRAO1_PIN 35  // Photoresistor and photodiod sensor pin
#define LDRAO2_PIN 32
#define LDRAO3_PIN 34
// #define LED_PIN 32 // Led pin
#define DDIR_PIN 4  // Driver pin
#define DSTEP_PIN 16
#define DENABLE_PIN 27
//
#define T_PIN15 T3
#define T_PIN12 T5


// WiFi details
const char* ssid = "Redmi";
const char* password = "123456789";
const char* test_root_ca =
  "-----BEGIN CERTIFICATE-----\n"
  "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\n"
  "-----END CERTIFICATE-----\n";

// MQTT broker details
const char* mqtt_server = "5c463a42551f40b4ba7f07a18da6866d.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_username = "mqtt123";
const char* mqtt_password = "HoangDepTrai123";

//
boolean flag = 0;
boolean auto_requests_state = 0;
boolean alarm_requests_state = 0;
int count = 0;
int numCircle;
int numCircleNow;
int numCircle1 = 0;
int numCircleS =0 ;
int status = -1;
int preStatus = -1;
int percent = -1;
int prePercent = 0;
String correlation_data, correlation_dataAlarm;
String message;
char buffer[64] = {};
const float GAMMA = 0.7;
const float RL10 = 50.0;
int touchValue12;
int touchValue15;
String outdoor, indoor;

// Initialize WiFi client and MQTT client
WiFiClientSecure wifiClient;
PubSubClient mqttClient(wifiClient);

// Callback function for receiving MQTT messages
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  message = "";
  Serial.print("Message: ");
  for (int i = 0; i < length; i++) {
    Serial.println((char)payload[i]);
    message += (char)payload[i];
  }
}

// Convert analog signal to Lux
float convertLux(int pin) {
  int analogValue = analogRead(pin);
  float voltage = analogValue / 4095.0 * 5;
  float resistance = 2000 * voltage / (1 - voltage / 5);
  float lux = pow(RL10 * 1e3 * pow(10, GAMMA) / resistance, (1 / GAMMA));
  return lux;
}

void setup() {

  // Start serial communication
  Serial.begin(115200);

  pinMode(DDIR_PIN, OUTPUT);
  pinMode(DSTEP_PIN, OUTPUT);
  pinMode(DENABLE_PIN, OUTPUT);
  pinMode(LDRAO1_PIN, INPUT);
  pinMode(LDRAO2_PIN, INPUT);
  pinMode(LDRAO3_PIN, INPUT);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
  wifiClient.setCACert(test_root_ca);

    // Set MQTT callback function
  mqttClient.setCallback(mqttCallback);

  // Connect to MQTT broker
  mqttClient.setServer(mqtt_server, mqtt_port);
  while (!mqttClient.connected()) {
    if (mqttClient.connect("ProjectIOT", mqtt_username, mqtt_password)) {
      Serial.println("Connected to MQTT broker!");
      mqttClient.subscribe("auto_requests");
      mqttClient.subscribe("alarm_requests");
    } else {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(mqttClient.state());
    }
  }

}

void loop() {
  // Reconect Wifi
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi!");
    wifiClient.setCACert(test_root_ca);
  }

  // Maintain connection to MQTT broker
  if (!mqttClient.connected()) {
    Serial.println("Reconnecting to MQTT broker...");
    while (!mqttClient.connected()) {
      if (mqttClient.connect("ProjectIOT", mqtt_username, mqtt_password)) {
        Serial.println("Connected to MQTT broker!");
        mqttClient.subscribe("alarm_requests");
        mqttClient.subscribe("auto_requests");
        JsonDocument doc6;
        char buffer[150];
        doc6["activate"] = true;
        serializeJson(doc6, buffer);
        mqttClient.publish("esp32_status", buffer);
      } else {
        Serial.print("Failed to connect to MQTT broker, rc=");
        Serial.print(mqttClient.state());
      }
    }
  }
  
  // Subscribe broker ///////////////////////////
  // // Arduino json 7.0 standard
    String temp;
    JsonDocument doc;
    if (mqttClient.subscribe("auto_requests")) auto_requests_state = 1;

    deserializeJson(doc, message);
    // if (doc["status"].as<String>() == "True")  status = 1;
    // else if (doc["status"].as<String>() == "False")   status = 0;
    if (doc["status"].as<boolean>() == true)  status = 1;
    else if (doc["status"].as<boolean>() == false)   status = 0;
    // percent = (doc["percent"].as<String>()).toInt();
    percent = (doc["percent"].as<int>());
    correlation_data = doc["correlation_data"].as<String>();
    if(mqttClient.subscribe("alarm_requests")) alarm_requests_state = 1;
    deserializeJson(doc, message);
    // percent = (doc["percent"].as<String>()).toInt();
    percent = (doc["percent"].as<int>());
    correlation_dataAlarm = doc["correlation_data"].as<String>();
    Serial.println(message);
  
  mqttClient.loop();
  ///////////////////////////////////////

  // Control Roller////////////////////////
  //---Setup---
  digitalWrite(DENABLE_PIN, LOW);
  touchValue12 = touchRead(T_PIN12);
  touchValue15 = touchRead(T_PIN15);

  if (touchRead(T_PIN12) < 20) {
    digitalWrite(DDIR_PIN, !digitalRead(DDIR_PIN));
  }

  digitalRead(DDIR_PIN) == 1 ? Serial.println("UP") : Serial.println("DOWN");
  while (touchValue15 < 20) {
    digitalWrite(DENABLE_PIN, LOW);
    digitalWrite(DSTEP_PIN, HIGH);
    delayMicroseconds(500);
    digitalWrite(DSTEP_PIN, LOW);
    delayMicroseconds(500);
    digitalRead(DDIR_PIN) == 1 ? numCircle++ : numCircle = 0;
    if (touchRead(T_PIN12) < 20) {
      digitalWrite(DENABLE_PIN, HIGH);
      numCircleNow = numCircle;
      percent = -1;
      break;
    }
    digitalRead(DDIR_PIN) == 1 ? Serial.println("UP") : Serial.println("DOWN");
  }
  //--------------------

  //---Control---
  if (numCircle > 0) {
    count == 1000?count = 2:count ++;
    int numCircleO = numCircle - numCircleNow; // the circle which change to open the curtain
    int numCircleC = numCircleNow; // the circle which change to close the curtain
    switch (status) {
      case 1 : {                                     // Automation
      Serial.println("Automation");
        if (digitalRead(LDRAO3_PIN) == HIGH && count > 1) {  // When it's Dark, closing
          outdoor = "Dark";
          for (int i = 0; i < numCircleC; i++) {
            digitalWrite(DDIR_PIN, LOW);
            digitalWrite(DSTEP_PIN, HIGH);
            delayMicroseconds(500);
            digitalWrite(DSTEP_PIN, LOW);
            delayMicroseconds(500);
          }
          numCircleNow = 0;
        } else if ((convertLux(LDRAO1_PIN) < 250) && (convertLux(LDRAO2_PIN) < 250) && digitalRead(LDRAO3_PIN) == LOW && count > 1) {
          outdoor = "Light";
          while ((numCircleO > 0) && (convertLux(LDRAO1_PIN) < 250) && (convertLux(LDRAO2_PIN) < 250)) {
            digitalWrite(DDIR_PIN, HIGH);
            digitalWrite(DSTEP_PIN, HIGH);
            delayMicroseconds(500);
            digitalWrite(DSTEP_PIN, LOW);
            delayMicroseconds(500);
            numCircleO--;
          }
          numCircleNow = numCircle - numCircleO;
        } else if (convertLux(LDRAO1_PIN) > 400 && (convertLux(LDRAO2_PIN) > 300) && count > 1) {
          while ((numCircleC > 0) && (convertLux(LDRAO1_PIN) > 400)) {
            digitalWrite(DDIR_PIN, LOW);
            digitalWrite(DSTEP_PIN, HIGH);
            delayMicroseconds(500);
            digitalWrite(DSTEP_PIN, LOW);
            delayMicroseconds(500);
            numCircleC--;
          }
          numCircleNow = numCircleC;
        }
        
        break;
      }
    case 0 : {  // Handle
      if (percent != prePercent && percent > 0) {
        int numCircleH = ((percent) * numCircle) / 100;
        if (numCircleH > numCircleNow ) {
          for (int i = 0; i < abs(numCircleNow - numCircleH); i++) {
            digitalWrite(DDIR_PIN, HIGH);
            digitalWrite(DSTEP_PIN, HIGH);
            delayMicroseconds(500);
            digitalWrite(DSTEP_PIN, LOW);
            delayMicroseconds(500);
            Serial.println ("ERR1");
          }
        } else if (numCircleH < numCircleNow) {
          for (int i = 0; i < abs(numCircleH - numCircleNow); i++) {
            digitalWrite(DDIR_PIN, LOW);
            digitalWrite(DSTEP_PIN, HIGH);
            delayMicroseconds(500);
            digitalWrite(DSTEP_PIN, LOW);
            delayMicroseconds(500);
            Serial.println ("ERR2");
          }
        }
        numCircleNow = numCircleH;
        break;
      }
    }
  }
  prePercent = percent;
}
indoor = convertLux(LDRAO1_PIN);

// Convert to Json and Publish


  JsonDocument doc2;
  doc2["indoor"] = String(indoor);
  doc2["outdoor"] = String(outdoor);
  doc2["ledState"] = "False";
  doc2["percent"] = String(prePercent);
  serializeJson(doc2, buffer);
  mqttClient.publish("inform", buffer);

  
  if(auto_requests_state == 1) {
    JsonDocument doc3;
    status == 1 ? doc3["status"] = true:doc3["status"] = false ;
    doc3["correlation_data"] = correlation_data;
    serializeJson(doc3, buffer);
    mqttClient.publish("auto_responses", buffer);
  }

  if (alarm_requests_state == 1) {
    JsonDocument doc4;
    doc4["status"] = true;
    doc4["auto_status"] = status;
    doc4["correlation_data"] = correlation_dataAlarm;
    serializeJson(doc4, buffer);
    mqttClient.publish("alarm_responses", buffer);
  }
  

delayMicroseconds(100);
}
