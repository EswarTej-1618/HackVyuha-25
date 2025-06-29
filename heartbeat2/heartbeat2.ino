#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const int PulseSensorHRWire = A0;
const int LED_A1 = A1;

int UpperThreshold = 550;
int LowerThreshold = 500;
int cntHB = 0;
boolean ThresholdStat = true;
int BPMval = 0;

unsigned long previousMillisGetHR = 0;
unsigned long previousMillisResultHR = 0;
const long intervalGetHR = 20;  // Check every 20ms
const long intervalResultHR = 10000;  // Calculate BPM every 10s

void setup() {
    pinMode(LED_A1, OUTPUT);
    Serial.begin(9600);

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

    // Read heartbeat signal
    if (currentMillis - previousMillisGetHR >= intervalGetHR) {
        previousMillisGetHR = currentMillis;
        int PulseSensorSignal = analogRead(PulseSensorHRWire);

        // Heartbeat detection
        if ((PulseSensorSignal > UpperThreshold) && ThresholdStat) {
            digitalWrite(LED_A1, HIGH);
            cntHB++;
            ThresholdStat = false;
        }

        if (PulseSensorSignal < LowerThreshold) {
            ThresholdStat = true;
            digitalWrite(LED_A1, LOW);
        }
    }

    // Calculate BPM without delay() blocking execution
    if (currentMillis - previousMillisResultHR >= intervalResultHR) {
        previousMillisResultHR = currentMillis;
        BPMval = cntHB * 6;  // Convert to BPM
        cntHB = 0;

        // Display BPM
        display.clearDisplay();
        display.setTextSize(2);
        display.setCursor(0, 10);
        display.print("BPM: ");
        display.println(BPMval);
        display.display();

        // Send BPM to Serial Monitor
        Serial.print("Heart Rate: ");
        Serial.print(BPMval);
        Serial.println(" BPM");
    }
}