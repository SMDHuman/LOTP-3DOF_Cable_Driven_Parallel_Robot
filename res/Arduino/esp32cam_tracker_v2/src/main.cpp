//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include <Arduino.h>
#include "esp_camera.h"
#include "serial_com.h"
#include "camera.h"
#include "beacon_com.h"
#include "tracker.h"

//-----------------------------------------------------------------------------
void led_init();
void led_task();

//-----------------------------------------------------------------------------
bool led_state;
bool stream_enable = false;
bool refresh_enable = true;

//-----------------------------------------------------------------------------
void setup() {
  led_init();
  serial_init();
  tracker_init();
  camera_init();
  beacon_init();
}

//-----------------------------------------------------------------------------
void loop() {
  serial_task();
  camera_task();
  beacon_task();
  tracker_task();
  led_task();
}

//-----------------------------------------------------------------------------
void led_init(){
  pinMode(33, OUTPUT);
}

//-----------------------------------------------------------------------------
void led_task(){
static uint64_t led_task_last;

  if(millis() - led_task_last > 0){
    digitalWrite(33, led_state);
    led_state = !led_state;
    //...
    led_task_last = millis();
  }
}