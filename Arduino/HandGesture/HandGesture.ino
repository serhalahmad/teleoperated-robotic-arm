#include <Servo.h>
#define numOfValsRec 5 // 5 fingers
#define digitsPerValRec 1 // the values in the array are gonna be 0 to 9

Servo servoThumb;
Servo servoIndex;
Servo servoMiddle;
Servo servoRing;
Servo servoPinky;

int valsRec[numOfValsRec]; //array containing the number of values received
int stringLength = numOfValsRec * digitsPerValRec + 1; //ex $00000 or $01001...
int counter = 0;
bool counterStart = false; //whenever we receive a $ sign, we will start the counter
String receivedString;

void setup() {
  Serial.begin(9600); // Initialize the serial

  // Attach the pins to each servo motor
  servoThumb.attach(2);
  servoIndex.attach(3);
  servoMiddle.attach(7);
  servoRing.attach(5);
  servoPinky.attach(6);
}

void receiveData(){
  while (Serial.available()){ // if there are data in the serial
    char c = Serial.read(); // reading character at a time from the serial
    if(c == '$'){
      counterStart = true;
    }
    if(counterStart){

      // Prepare the array for the servos
      if(counter < stringLength){
        receivedString = String(receivedString + c);
        counter++;
      }
      if(counter >= stringLength){
        for(int i = 0; i < numOfValsRec; i++){
          int num = (i * digitsPerValRec) + 1;
          valsRec[i] = receivedString.substring(num,num + digitsPerValRec).toInt();
        }
        receivedString = "";
        counter = 0;
        counterStart = false;
      }
    }
  }
}

void loop() {
  delay(500); // waiting 0.5sec between each iteration
  receiveData(); // prepare the data for the servos
  
  // Scaling the data received to have them as angles ready to be written to the servos
  for (int i = 0; i < 5; i++){
    if(i == 0 || i == 1 || i == 2){
      valsRec[i] = (180 - 120) * (valsRec[i] - 0) / 10 + 120;   
    } else if(i == 3 || i == 4){
      valsRec[i] = (90 - 0) * (valsRec[i] - 0) / 10 + 0;   
    }
  }
  
  servoThumb.write(valsRec[0]);
  servoIndex.write(valsRec[1]);
  servoMiddle.write(valsRec[2]);
  servoRing.write(90 - valsRec[3]);
  servoPinky.write(90 - valsRec[4]);

  // if no data is received, open all the fingers
  for (int i = 0; i < 5; i++){
    valsRec[i] = 9;
  }
  
}
