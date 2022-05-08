

#include <Arduino.h>

#define SERVO_PULSE_GPIO        (25)   // GPIO connects to the PWM signal line
#define SERVO_ENABLE_GPIO       (26)   
#define SERVO_ERROR_GPIO        (35)   
#define SERVO_DIRECTION_GPIO    (18)   
#define SERVO_BRAKE             (22)
#define LV_3V                   (19) // we are using a step-up, this is 3.3v
#define LV_GND                  (23)
#define ESP_INTR_FLAG_DEFAULT 0  


// 23, 32 is ground
// 33, 19 3.3

#define PWM1_Ch    2
#define PWM1_Res   8
#define PWM1_Freq  400
#define PWM2_Ch    3
#define PWM2_Res   16
#define PWM2_Freq  20

#define LD27MG_0_DEGREES    500
#define LD27MG_270_DEGREES  2500

class Anchorer
{
  public:
  Anchorer(){
    anchor_enable_ = false;
    anchor_forward_ = false;
    anchor_error_ = false;
    frequency_ = PWM1_Freq;
    
    pinMode(LV_3V, OUTPUT);
    pinMode(LV_GND, OUTPUT);
    pinMode(SERVO_ERROR_GPIO, INPUT);
    pinMode(SERVO_ENABLE_GPIO, OUTPUT);
    pinMode(SERVO_DIRECTION_GPIO, OUTPUT);
    ledcSetup(PWM1_Ch, PWM1_Freq, PWM1_Res);
    ledcAttachPin(SERVO_PULSE_GPIO, PWM1_Ch);
    // brake
    ledcSetup(PWM2_Ch, PWM2_Freq, PWM2_Res); // channel 1, 50 Hz, 16-bit width
    ledcAttachPin(SERVO_BRAKE, PWM2_Ch);   // GPIO 22 assigned to channel 1
  }
  

  void move_forward(void){
    anchor_enable_ = true;
    anchor_forward_ = true;
  }
  
  void stop_movement(void){
    anchor_enable_ = false;
    anchor_forward_ = false;
  }

  void anchorer_tick(void){
  }
  
  void tick_server(){
    
    digitalWrite(SERVO_ENABLE_GPIO, anchor_enable_);
    digitalWrite(LV_3V, true);
    digitalWrite(LV_GND, false);
    
//    for (int i=LD27MG_0_DEGREES ; i < LD27MG_270_DEGREES ; i=i+100)
//    {
//      ledcWrite(PWM2_Ch, i);       // sweep servo 1
//      vTaskDelay(200);
//    }
    while(true){
      ledcWrite(PWM1_Ch, 128); // duty cycle between 0-255
      digitalWrite(SERVO_ENABLE_GPIO, anchor_enable_);
      digitalWrite(SERVO_DIRECTION_GPIO, anchor_forward_);
      anchor_error_ = digitalRead(SERVO_ERROR_GPIO);
      vTaskDelay(15);
      Serial.println("tick_anchorer");
    }
  }
  // dumb workaround
  static void tick_server_static(void* pvParameters){
    Anchorer *l_pThis = (Anchorer *) pvParameters;
    l_pThis->tick_server();
  }
  private:
    bool anchor_enable_;
    bool anchor_forward_;
    bool anchor_error_;
    int frequency_;
};
