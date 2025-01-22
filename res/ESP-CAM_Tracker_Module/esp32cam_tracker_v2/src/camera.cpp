//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "camera.h"
#include "serial_com.h"
#include "beacon_com.h"
#include "tracker.h"

//-----------------------------------------------------------------------------
capture_mode_e camera_capture_mode = ONESHOT;
bool camera_trigger;
uint64_t fb_log_last;
uint64_t camera_width;
uint64_t camera_height;

//-----------------------------------------------------------------------------
void camera_init(){
  esp_err_t err = esp_camera_init(&camera_config);
  if(err == -1){
    Serial.println("Failed to initialize camera!!");
    return;
  }
  sensor_t * s = esp_camera_sensor_get();
  // 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale ...
  s->set_special_effect(s, 2); 
}
//-----------------------------------------------------------------------------
void camera_task(){
  uint64_t task_start = millis();
  static uint64_t last_camera_report;
  //...
  camera_fb_t *fb = esp_camera_fb_get(); // get fresh image
  camera_width = fb->width;
  camera_height = fb->height;
  //...
  if(!fb){
    Serial.println("Couldn't get frame buffer!");
    return;
  }
  if(tracker_status == WAIT){
    push_camera_buffer(fb);
    tracker_status = READY;
  }
  //...
  if((camera_capture_mode == ONLED) & camera_trigger){
    send_image(fb->width, fb->height, fb->buf, fb->len);
    camera_trigger = false;
  }
  //...
  if((camera_capture_mode == ONESHOT) & camera_trigger){
    send_image(fb->width, fb->height, fb->buf, fb->len);
    camera_trigger = false;
  }
  //...
  if(camera_capture_mode == STREAM){
    send_image(fb->width, fb->height, fb->buf, fb->len);
  }
  //...
  esp_camera_fb_return(fb);
  //...
  uint64_t task_end = millis();
  #ifdef DEBUG
  if(last_camera_report - task_end > 200){
    Serial.print("Camera Task ms: ");
    Serial.println(task_end - task_start);
    last_camera_report = task_end;
  }
  #endif
}
