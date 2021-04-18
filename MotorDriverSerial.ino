#include <analogWrite.h>
#define MOTOR_PWM 27
#define MOTOR_DIRECTION 14
#define ENCODER_INTERRUPT 13
#define MOTOR_SPEED 250
#define COUNT_VALUE 8
#define LED 2
#define MOTOR_STATE_FLAG_1 25
#define MOTOR_STATE_FLAG_2 33

uint32_t MOTOR_3DEGREE_COUNTER = 1294;
uint32_t MOTOR_5DEGREE_COUNTER = 2157;
uint32_t MOTOR_90DEGREE_COUNTER = 32355;

unsigned long now,op_time_last;
bool motor_direction_bool;
bool pinstate =false;
uint8_t motor_speed;
uint32_t operation_timer;
uint8_t ReceivedSerial = 0;
uint8_t status_flag[1];
bool motorStateFlag1 = false;
bool motorStateFlag2 = false;
uint8_t  NO_ACTION =0;
uint8_t  CHECK_AVAILABLITY = 1;
uint8_t  MOTOR_RIGHT_3 = 2;
uint8_t  MOTOR_LEFT_3 = 3;
uint8_t  MOTOR_RIGHT_5 = 4;
uint8_t  MOTOR_LEFT_90 = 5;

//raspberry commands list for ReceivedSerial variable
//0 = no action
//1 = check if the esp32 is available to action
//2 = send command to run motor to right to correction
//3 = send command to run motor to left to correction
//4 = send command to run motor right to make routine operation to right
//5 = send command to run motor to reverse for next day

//esp responses list for actions
//6 = avalibility check value
//7 = motor action finished successfully

void Motor_Run(uint8_t motor_speed, bool motor_direction_bool);
void Motor_Stop(void);
void ledToggle(void);

 
void setup() {
  Serial.begin(115200);
  //pinMode(ENCODER_INTERRUPT, INPUT_PULLUP);
  pinMode(MOTOR_PWM, OUTPUT);
  pinMode(MOTOR_DIRECTION, OUTPUT);
  pinMode(MOTOR_STATE_FLAG_1, INPUT);
  pinMode(MOTOR_STATE_FLAG_2, INPUT);
  pinMode(LED, OUTPUT);
  //attachInterrupt(digitalPinToInterrupt(ENCODER_INTERRUPT),encoder_count,FALLING);
  //digitalPinToInterrupt(13);
  }

void loop() {
    ReceivedSerial = Serial.read() - '0';
    if (ReceivedSerial <= 200){
      if(ReceivedSerial == CHECK_AVAILABLITY){
        ledToggle();
        Serial.println("6");      
        ReceivedSerial = 0;
        }
      if(ReceivedSerial == MOTOR_RIGHT_3){
        Serial.println("6");
        ledToggle();
        operation_timer = MOTOR_3DEGREE_COUNTER; 
        ReceivedSerial = 0;     
        Motor_Run(MOTOR_SPEED,true); 
        delay(operation_timer);
        Motor_Stop(); 
        }      
      if(ReceivedSerial == MOTOR_LEFT_3){
        Serial.println("6"); 
        ledToggle();     
        operation_timer = MOTOR_3DEGREE_COUNTER;
        ReceivedSerial = 0;
        Motor_Run(MOTOR_SPEED,false);
        delay(operation_timer);
        Motor_Stop(); 
        }  
      if(ReceivedSerial == MOTOR_RIGHT_5){
        ReceivedSerial = 0;
        Serial.println("6");
        ledToggle();
        operation_timer = MOTOR_5DEGREE_COUNTER;
        Motor_Run(MOTOR_SPEED,true);
        delay(operation_timer);
        Motor_Stop(); 
        }
      if(ReceivedSerial == MOTOR_LEFT_90){
        Serial.println("6");
        ReceivedSerial = 0;
        ledToggle();
        operation_timer = MOTOR_90DEGREE_COUNTER;      
        Motor_Run(MOTOR_SPEED,false);
        delay(operation_timer);
        Motor_Stop(); 
        } 
    } 
}


void Motor_Run(uint8_t motor_speed, bool motor_direction){
  now = millis();
  motorStateFlag1 = digitalRead(MOTOR_STATE_FLAG_1);
  motorStateFlag2 = digitalRead(MOTOR_STATE_FLAG_2);
  motorStateFlag1 = false;
  motorStateFlag2 = false;
  if(motorStateFlag1 == false && motorStateFlag2 == false && ((now - op_time_last) >= 150000)){
    digitalWrite(MOTOR_DIRECTION, motor_direction);
    analogWrite(MOTOR_PWM,motor_speed);
    op_time_last = millis();
  }
   else{
    digitalWrite(MOTOR_DIRECTION, true);
    analogWrite(MOTOR_PWM,0);
    }    
 }

void Motor_Stop(){
  motor_speed = 0;
  Motor_Run(motor_speed,true);
  }

//void encoder_count(){
//  if(pinstate == false){
//    digitalWrite(LED, HIGH);
//    pinstate = true;}
//  else if(pinstate == true){
//    digitalWrite(LED, LOW);
//    pinstate = false;}
//  Serial.println(operation_timer);
//  operation_timer--;
//  if (operation_timer == 0){
//  Serial.println("counter0");
//    Motor_Stop(); 
//  }
//} 

void ledToggle(){
    if(pinstate == false){
    digitalWrite(LED, HIGH);
    pinstate = true;}
    else if(pinstate == true){
    digitalWrite(LED, LOW);
    pinstate = false;}}
