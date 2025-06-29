
// Motor A (Left Motor)
const int ENA  = 5;    
const int IN1  = 7;    
const int IN2  = 8;    

// Motor B (Right Motor)
const int ENB  = 6;    
const int IN3  = 3;    
const int IN4  = 4;    

// Ultrasonic Sensors
#define trig1 2    // Front sensor trig
#define echo1 10   // Front sensor echo
#define trig2 11   // Rear sensor trig
#define echo2 12   // Rear sensor echo

unsigned long lastDistancePrintTime = 0;
const unsigned long distancePrintInterval = 1000; // 1 second


void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void moveReverse() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  
}

void turnRight() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH); 
  digitalWrite(IN4, HIGH);
  digitalWrite(IN3, LOW); 

}

void turnLeft() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW); 
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW); 
}

void stopMoving() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}


// Ultrasonic Distance Reading

long getDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  return pulseIn(echoPin, HIGH) * 0.034 / 2;
}

// Obstacle Avoidance 

void avoidObstacle() {
  Serial.println("Obstacle detected! Executing avoidance...");
  stopMoving();
  delay(300);

  turnRight(); delay(400);
  moveForward(); delay(300);
  turnLeft(); delay(500);
  moveForward(); delay(500);
   turnLeft(); delay(500);
    moveForward(); delay(300);
    turnRight(); delay(400);
  stopMoving();
}

void setup() {
  Serial.begin(9600);

  // Motor pins
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Ultrasonic pins
  pinMode(trig1, OUTPUT); 
  pinMode(echo1, INPUT);
  pinMode(trig2, OUTPUT); 
  pinMode(echo2, INPUT);

  // Enable motors
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);

  Serial.println("Chassis Controller Initialized");
}

void loop() {
  // Read front distance
  long frontDist = getDistance(trig1, echo1);

  // Always avoid obstacle if too close
  if (frontDist < 20) {
    avoidObstacle();
  }

  // Print distances every 1 second
  if (millis() - lastDistancePrintTime >= distancePrintInterval) {
    lastDistancePrintTime = millis();

    long backDist = getDistance(trig2, echo2);

    Serial.print("Front Distance: ");
    Serial.print(frontDist);
    Serial.print(" cm, ");

    Serial.print("Back Distance: ");
    Serial.print(backDist);
    Serial.println(" cm");
  }

  // Handle Bluetooth input
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();

    if (data.length() > 0) {
      Serial.print("Received: ");
      Serial.println(data);

      int commaIndex = data.indexOf(',');
      if (commaIndex != -1) {
        String blinkStr = data.substring(0, commaIndex);
        String gazeStr  = data.substring(commaIndex + 1);
        blinkStr.trim();
        gazeStr.trim();

        int blinkCount = blinkStr.toInt();

        if (gazeStr != "None") {
          if (gazeStr == "Looking Left") {
            Serial.println("Executing Turn: Left");
            turnLeft(); delay(500);
            stopMoving();
          } else if (gazeStr == "Looking Right") {
            Serial.println("Executing Turn: Right");
            turnRight(); delay(500);
            stopMoving();
          }
        } else {
          if (blinkCount == 1) {
            if (frontDist >= 30) {
              moveForward();
              Serial.println("Action: Move Forward");
            } 
            else if(frontDist<30 && frontDist>0){
              avoidObstacle();
            }
            else {
              Serial.println("Blocked! Front too close.");
              stopMoving();
            }
          } else if (blinkCount == 2) {
            stopMoving();
            Serial.println("Action: Stop");
          } else if (blinkCount == 3) {
              moveReverse();
              Serial.println("Action: Move Reverse");
             delay(500);
              stopMoving();
            }
          }
        }
      } else {
        Serial.println("Error: Incorrect format. Use 'blinkCount,gazeCommand'");
      }
    }
  }

