#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SoftwareSerial.h>  // Include this library

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Use pins 2 and 3 for SoftwareSerial (RX, TX)
SoftwareSerial BTSerial(2, 3); // RX = 2, TX = 3

unsigned long previousMillisGetHR = 0;
unsigned long previousMillisResultHR = 0;

const long intervalGetHR = 20;
const long intervalResultHR = 10000;

int PulseSensorSignal;
const int PulseSensorHRWire = A0;
const int LED_A1 = A1;

int UpperThreshold = 550;
int LowerThreshold = 500;

int cntHB = 0;
boolean ThresholdStat = true;
int BPMval = 0;

int x = 0;
int y = 0;
int lastx = 0;
int lasty = 0;

void setup() {
  pinMode(LED_A1, OUTPUT);
  Serial.begin(9600);      // Serial Monitor
  BTSerial.begin(9600);    // Bluetooth (SoftwareSerial)

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.display();
}

void loop() {
  unsigned long currentMillis = millis();

  // Read heartbeat signal every 20 ms
  if (currentMillis - previousMillisGetHR >= intervalGetHR) {
    previousMillisGetHR = currentMillis;
    PulseSensorSignal = analogRead(PulseSensorHRWire);

    // Map signal to display height (for graphing)
    y = map(PulseSensorSignal, 0, 1023, SCREEN_HEIGHT, 0);
    x++;
    if (x > SCREEN_WIDTH) {
      x = 0;
      display.clearDisplay();                                      
    }

    // Plot graph
    display.drawLine(lastx, lasty, x, y, SSD1306_WHITE);
    lastx = x;
    lasty = y;

    // Heartbeat detection
    if ((PulseSensorSignal > UpperThreshold) && ThresholdStat) {
      digitalWrite(LED_A1, HIGH);
      cntHB++;
      ThresholdStat = false;
    }

    if (PulseSensorSignal < LowerThreshold) {
      ThresholdStat = true;
      digitalWrite(LED_A1, LOW)
    }
  }

  // Calculate BPM every 10 seconds
  if (currentMillis - previousMillisResultHR >= intervalResultHR) {
    previousMillisResultHR = currentMillis;
    BPMval = cntHB * 6; // 10 sec interval, so multiply by 6 for 60 sec
    cntHB = 0;

    // Display BPM
    display.clearDisplay();
    display.setTextSize(2);
    display.setCursor(0, 10);
    display.print("BPM: ");
    display.println(BPMval);
    display.display();

    // Send BPM to Serial Monitor and Bluetooth (HC-05)
    Serial.print("Heart Rate: ");
    Serial.print(BPMval);
    Serial.println(" BPM");

    BTSerial.print("Heart Rate: ");
    BTSerial.print(BPMval);
    BTSerial.println(" BPM");

    delay(3000); // Show BPM for 3 seconds
    display.clearDisplay();
    x = 0;
    lastx = 0;
  }

  display.display();
}