#include <Arduino.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WiFiClientSecure.h>
#include <AccelStepper.h>

// Xác định chiều quay motor DIR
const int DIR_PIN = 4;
// Xác định tốc độ quay của motor, mỗi xung bằng quay 1 bước (STEP) 
const int STEP_PIN = 16;
// Bật/Tắt nguồn motor để tiết kiệm điện
const int ENABLE_PIN = 21;
// Cảm biến ánh sáng, 2 cái đầu để đo nhiệt độ phòng, cái thứ 3 đo nhiệt độ ngoài trời
const int LDR_A1_PIN = 34;
const int LDR_A2_PIN = 14;
// Cảm biến thứ 3 sử dụng chân digital, khi trời tối là HIGH, trời sáng là LOW
const int LDR_D1_PIN = 12;
// Công tắc đèn của phòng
const int LED_PIN = 33;

//---------------Thông số ---------------------
const int SERIAL_BAUD = 11520;
const int INTERVAL = 1000; // Sau 1s gửi 1 message lên topic inform

//---------------Thiết lập broker----------------------
// Thực tế thay tên wifi và password của bạn vào
const char* ssid = "<YOUR_WIFI>";
const char* password = "<YOUR_PASSWORD>";
const char* test_root_ca =
  "-----BEGIN CERTIFICATE-----\n"
  "<YOUR_BROKER_CA>"
  "-----END CERTIFICATE-----\n";

const char* mqtt_server = "<URI_MQTT_BROKER>";
const int mqtt_port = 8883;
const char* mqtt_username = "<YOUR_USERNAME>";
const char* mqtt_password = "<YOUR_PASSWORD>";
const char* lwt_topic = "esp32_status";
const int lwt_qos = 1;
const char* lwt_message = "{\"activate\": false}";
const bool lwt_retain = true;

WiFiClientSecure wiFiClient;
PubSubClient client(wiFiClient);

//------------SET UP WFI and Broker--------------
void setupWiFi(){
  WiFi.begin(ssid, password);
  Serial.println("--------Wait for WiFi--------");
  while(WiFi.status() != WL_CONNECTED){
    delay(5000);
    Serial.println("Connecting to WiFi ...");
    WiFi.disconnect();
    WiFi.reconnect();
  }
  Serial.println("WiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnectBroker(){
  setupWiFi();
  wiFiClient.setCACert(test_root_ca);
  Serial.println("-------Connecting to hivemq cloud-------");
  while (!client.connected()){
    if(client.connect("Project IOT", mqtt_username, mqtt_password, lwt_topic, lwt_qos, lwt_retain, lwt_message)){
      JsonDocument doc;
      doc["activate"] = true;
      char buf[64];
      // Hàm serializeJson chuyển đổi đối tượng doc thành chuỗi json vào buff
      serializeJson(doc, buf);
      client.publish("esp32_status", buf, true);

      client.subscribe("handle_requests");
      client.subscribe("auto_requests");
      Serial.println("Successful connect to MQTT broker!");
    }else{
      Serial.print("Failed to connected to MQTT broker, rc= ");
      Serial.print(client.state());
      Serial.println("Retrying in 5 seconds...");
      delay(4000);
    }
  }
}

//----------------init pin------------------------------
void initPin(){
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);

  pinMode(LDR_A1_PIN, INPUT);
  pinMode(LDR_A2_PIN, INPUT);
  pinMode(LDR_D1_PIN, INPUT);

  pinMode(LED_PIN, INPUT);
}
//------------Convert analog signal of LDRAO to Lux--------------
const float GAMMA = 0.7;
const float RL10 = 50.0;

float convertLux(int ldr_pin) {
  int analogValue = analogRead(ldr_pin);
  float voltage = analogValue / 4095.0 * 5;
  float resistance = 2000 * voltage / (1 - voltage / 5);
  float lux = pow(RL10 * 1e3 * pow(10, GAMMA) / resistance, (1 / GAMMA));
  return lux;
}

// ---------Biến global cho xử lý toàn bộ logic---------
bool outdoor; // 0 là sáng 1 là tối
float indoor;
bool ledState;
float current_percent = 0;

const int max_step = 300;
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN, ENABLE_PIN);

float target_percent;
bool auto_status = false;

//----------Lấy thông tin trạng thái phòng--------------
void collectRoomInform(){
  indoor = convertLux(LDR_A1_PIN);
  // Cảm biến ánh sáng 3 trên hoặc bằng 100 lux trả về 0, dưới 100 lux trả về 1
  outdoor = digitalRead(LDR_D1_PIN);
  ledState = digitalRead(LED_PIN);
  current_percent = map(stepper.currentPosition(), 0, max_step, 0, 100);
}

//----------Publish trạng thái phòng lên broker ------------
unsigned long previousMillis = 0;      // Biến lưu trữ thời gian gần nhất publish message lên topic = "inform"
char buffer[512];

void publishRoomInform(){
 unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    previousMillis = currentMillis; // Lưu thời gian hiện tại
    JsonDocument doc;
    doc["indoor"] = indoor;
    if (!outdoor){
      doc["outdoor"] = String("LIGHT");
    } else {
      doc["outdoor"] = String("DARK");
    }
    doc["ledState"] = ledState;
    doc["percent"] = current_percent;
    serializeJson(doc, buffer);

    client.publish("inform", buffer);
  }
}

//------------Handle Mode----------
// Hàm chỉ mang tính chất định hướng target của stepper, phải kết hợp run() trong hàm loop()
void handle_mode(){
  if (current_percent!=target_percent){
    if (current_percent < target_percent){
      if (stepper.currentPosition() < max_step){
        stepper.move(1);
        current_percent = map(stepper.currentPosition(), 0, max_step, 0, 100);
      }
    } else{
      if (stepper.currentPosition() > 0){
        stepper.move(-1);
        current_percent = map(stepper.currentPosition(), 0, max_step, 0, 100);
      }
    }
  }
}

//------------Auto Mode---------
// Hàm sẽ dịch lên/xuống 1 bước mỗi lần thầy ánh sáng ko thỏa mãn
// Kết hợp với vòng loop sẽ làm chương trình nhanh hơn
// Sự khác mạnh move() và moveTo(): 
    // khi gọi hàm run() nó cảnh báo động cơ sẽ phải chạy do có move() và moveTo() chứ không phải mỗi lần run() sẽ
      // chạy 1 step, nó chạy theo gia tốc và maxspeed đã cài => run() luôn ở trong vòng loop() hoặc while()
    // cả 2 hàm đều là bất động bộ do trên
void auto_mode(){
  if (!outdoor){ //Khi trời sáng
    if (ledState){ // Nếu đèn trong phòng bật, mặc định giữ nguyên vị trí rèm hoặc dừng rèm lại
      stepper.stop();
    } else{ // Nếu không có đèn thực hiện thuật toán auto dựa vào dữ liệu LDROA01_PIN và LDROA02_PIN
      if (convertLux(LDR_A1_PIN) < 250 && convertLux(LDR_A2_PIN) < 250){
        // Nếu độ sáng trong phòng quá nhỏ thì di chuyển rèm lên 1 step
        if (stepper.currentPosition() < max_step){
          stepper.move(1);
          current_percent = map(stepper.currentPosition(), 0, max_step, 0, 100);
        }
      }else {
        // Nếu độ sáng trong phòng quá sáng thì hạ rèm xuống 1 step
        if (convertLux(LDR_A1_PIN) > 400 && convertLux(LDR_A2_PIN) > 300){
          if (stepper.currentPosition() > 0){
            stepper.move(-1);
            current_percent = map(stepper.currentPosition(), 0, max_step, 0, 100);
          }
        }
      }
    }
  } else { // Khi trời tối mặc định đóng rèm
    if(current_percent > 0){
      stepper.move(-1);
      current_percent = map(stepper.currentPosition(), 0, max_step, 0, 100);
    }
  }
}
//------------Handle message from broker--------------
void handle_requests(JsonDocument& doc){
  // Xử lý request
  // Khi handle tự động tắt chế độ auto
  auto_status = false;
  target_percent = doc["percent"].as<int>();

  // Sau khi xử lý xong tạo response trả về
  JsonDocument response;
  response["auto_status"] = auto_status;
  response["correlation_data"] = doc["correlation_data"].as<String>();
  char buf[256];
  serializeJson(response, buf);

  client.publish("handle_responses", buf);
}

void auto_requests(JsonDocument& doc){
  // Xử lý request
  auto_status = doc["auto_status"].as<bool>();

  // Sau xử lý tạo response trả về
  JsonDocument response;
  response["auto_status"] = auto_status;
  response["correlation_data"] = doc["correlation_data"].as<String>();
  char buf[128];
  serializeJson(response, buf);

  client.publish("auto_responses", buf);
}

void callback(char* topic, byte* payload, unsigned int length){
  Serial.println("Received message from topic: "+ String(topic));
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Message: " + message);

  JsonDocument doc;
  deserializeJson(doc, message);
  if (String(topic) == "handle_requests"){
    handle_requests(doc);
    Serial.println("Successful proccess message has correlation_data: "+ doc["correlation_data"].as<String>());
  }else if (String(topic) == "auto_requests"){
    auto_requests(doc);
    Serial.println("Successful proccess message has correlation_data: "+ doc["correlation_data"].as<String>());
  }else {
    Serial.println("----------------------------------------------------");
    Serial.println("Faild to process message from topic: "+ String(topic));
    Serial.println(message);
    Serial.println("----------------------------------------------------");
  }
}

//-----------------------------------------------------
void setup() {
  Serial.begin(115200);
  initPin();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  reconnectBroker();

  stepper.setMaxSpeed(100);
  stepper.setAcceleration(50);
  // Do Motor của wokwi bắt đầu từ -2, thực tế không cần cái này
  stepper.runToNewPosition(2);

  stepper.setCurrentPosition (0);
  Serial.println("-------Start Processs-------");
}

void loop() {
  while(!client.connected()){
    reconnectBroker();
  }

  collectRoomInform();
  publishRoomInform();
  client.loop();

  // Rèm thông minh
  if(auto_status){
    auto_mode();
  }else {
    handle_mode();
  }

  if (stepper.distanceToGo() != 0) {
    stepper.run();
  } else {
    //Nếu rèm không cần thay đổi tắt di cho tiết kiệm điện
    stepper.stop();
  }

  delay(100);
}