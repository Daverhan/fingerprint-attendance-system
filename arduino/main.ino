#include <Adafruit_Fingerprint.h>
#include <WiFiS3.h>
#include <ArduinoHttpClient.h>
#include "arduino_secrets.h"

#define mySerial Serial1
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

uint32_t organizationID = 0;
String organizationPIN = "";
uint32_t eventID = 0;
const char* wifiSSID = SECRET_SSID;
const char* wifiPassword = SECRET_PASSWORD;
int wifiStatus = WL_IDLE_STATUS;
const char* serverIP = SERVER_IP;
const int serverPort = SERVER_PORT;

WiFiClient wifiClient;
HttpClient client = HttpClient(wifiClient, serverIP, serverPort);

void setup() {
  Serial.begin(9600);
  delay(100);
  mySerial.begin(57600);
  finger.begin(57600);

  if (!finger.verifyPassword()) {
    Serial.println("Error: Fingerprint sensor not found");
    while (1) { delay(1); }
  }

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Error: Communication with WiFi module failed");
    while (1) { delay(1); }
  }

  verifyWiFiConnection();
}

void loop() {
  uint8_t choice;

  displayMenu();
  choice = readNumber();

  switch (choice) {
    case 1:
      configureSettings();
      break;
    case 2:
      enrollNewMember();
      break;
    case 3:
      activateContinuousEventCheckin();
      break;
  }
}

void verifyWiFiConnection() {
  while (wifiStatus != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(wifiSSID);

    wifiStatus = WiFi.begin(wifiSSID, wifiPassword);

    delay(10000);
  }
}

void displayMenu() {
  Serial.println("\n@=== Fingerprint Attendance System ===@");
  Serial.println("1) Configure Organization and Event");
  Serial.println("2) Enroll New Member");
  Serial.println("3) Activate Continuous Event Check-in");
}

uint32_t readNumber() {
  uint32_t number = 0;

  while (number == 0) {
    while (!Serial.available())
      ;
    number = Serial.parseInt();
  }

  return number;
}

String readString() {
  String string = "";

  while (string == "") {
    while (!Serial.available())
      ;
    string = Serial.readString();
  }

  return string;
}

void configureSettings() {
  Serial.println("\n@=== Configure Organization and Event ===@");

  Serial.println("Enter Organization ID");
  organizationID = readNumber();

  Serial.println("Enter Organization PIN");
  organizationPIN = readString();

  verifyWiFiConnection();

  String jsonPayload = "{\"pin\":\"" + organizationPIN + "\"}";

  client.beginRequest();
  client.post("/organizations/" + String(organizationID) + "/verify-pin");
  client.sendHeader("Content-Type", "application/json");
  client.sendHeader("Content-Length", jsonPayload.length());
  client.beginBody();
  client.print(jsonPayload);
  client.endRequest();

  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  if (statusCode == 404) {
    Serial.println("Error: The provided organization does not exist");
    return;
  } else if (statusCode != 200) {
    Serial.println(response);
    return;
  }

  Serial.println("Enter Event ID");
  eventID = readNumber();

  Serial.print("\nOrganization ID: ");
  Serial.println(organizationID);
  Serial.print("Event ID: ");
  Serial.println(eventID);
}

void enrollNewMember() {
  String firstName, lastName;
  uint32_t fingerprintID;

  Serial.println("\n@=== Enroll New Member ===@");

  Serial.println("Enter First Name");
  firstName = readString();

  Serial.println("Enter Last Name");
  lastName = readString();

  fingerprintID = getNextAvailableFingerprintID();

  Serial.print("\nFirst Name: ");
  Serial.println(firstName);
  Serial.print("Last Name: ");
  Serial.println(lastName);
  Serial.print("Fingerprint ID: ");
  Serial.println(fingerprintID);

  while (getFingerprintEnroll(fingerprintID) != FINGERPRINT_OK)
    ;

  verifyWiFiConnection();

  String jsonPayload = "{\"first_name\":\"" + firstName + "\",\"last_name\":\"" + lastName + "\",\"fingerprint_device_id\":" + String(fingerprintID) + "}";

  client.beginRequest();
  client.post("/organizations/" + String(organizationID) + "/create_member");

  client.sendHeader("Content-Type", "application/json");
  client.sendHeader("Content-Length", jsonPayload.length());
  client.beginBody();
  client.print(jsonPayload);
  client.endRequest();

  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.println(response);

  if (statusCode != 200) {
    return;
  }
}

void activateContinuousEventCheckin() {
  Serial.println("\n@=== Activating Continuous Event Check-in ===@");
  Serial.println("Enter the letter 'q' to stop continuously scanning fingerprints");

  while (1) {
    getFingerprintIDez();
    delay(50);

    if (Serial.available() > 0) {
      char key = Serial.read();
      if (key) {
        break;
      }
    }
  }
}

uint16_t getNextAvailableFingerprintID() {
  uint8_t p;

  finger.getParameters();

  for (uint16_t id = 1; id <= finger.capacity; id++) {
    p = finger.loadModel(id);

    if (p == FINGERPRINT_NOTFOUND || p == 12) {
      return id;
    }
  }

  return 0;
}

uint8_t getFingerprintEnroll(uint32_t id) {
  int p = -1;
  Serial.print("Waiting for valid finger to enroll as #");
  Serial.println(id);
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image taken");
        break;
      case FINGERPRINT_NOFINGER:
        Serial.print(".");
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error");
        break;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error");
        break;
      default:
        Serial.println("Unknown error");
        break;
    }
  }

  p = finger.image2Tz(1);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }

  Serial.println("Remove finger");
  delay(2000);
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }
  Serial.print("ID ");
  Serial.println(id);
  p = -1;
  Serial.println("Place same finger again");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image taken");
        break;
      case FINGERPRINT_NOFINGER:
        Serial.print(".");
        break;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error");
        break;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error");
        break;
      default:
        Serial.println("Unknown error");
        break;
    }
  }

  p = finger.image2Tz(2);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }

  Serial.print("Creating model for #");
  Serial.println(id);

  p = finger.createModel();
  if (p == FINGERPRINT_OK) {
    Serial.println("Prints matched!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_ENROLLMISMATCH) {
    Serial.println("Fingerprints did not match");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }

  Serial.print("ID ");
  Serial.println(id);
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.println("Stored!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_BADLOCATION) {
    Serial.println("Could not store in that location");
    return p;
  } else if (p == FINGERPRINT_FLASHERR) {
    Serial.println("Error writing to flash");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }

  return p;
}

int getFingerprintIDez() {
  uint8_t p = finger.getImage();

  if (p == FINGERPRINT_NOFINGER) return -1;

  p = finger.image2Tz();

  if (p != FINGERPRINT_OK) {
    Serial.println("Error: Please try scanning your fingerprint again");
    return -1;
  }

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK) {
    Serial.println("Error: The scanned fingerprint is not enrolled");
    return -1;
  }

  verifyWiFiConnection();

  client.beginRequest();
  client.post("/organizations/" + String(organizationID) + "/events/" + String(eventID) + "/check-in/" + String(finger.fingerID));
  client.endRequest();

  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.println(response);

  if (statusCode != 200) {
    return -1;
  }

  return finger.fingerID;
}