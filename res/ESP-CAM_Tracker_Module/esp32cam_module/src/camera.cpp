//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "camera.h"
#include "serial_com.h"

//-----------------------------------------------------------------------------
capture_mode_e camera_capture_mode = ONESHOT;
bool camera_trigger;
uint64_t fb_log_last;

//-----------------------------------------------------------------------------
void camera_init(){
  esp_err_t err = esp_camera_init(&camera_config);
  if(err == -1){
    Serial.println("Failed to initialize camera!!");
    return;
  }
}
//-----------------------------------------------------------------------------
void camera_task(){
  camera_fb_t *fb = esp_camera_fb_get(); // get fresh image
  //...
  if(!fb){
    Serial.println("Couldn't get frame buffer!");
    return;
  }
  //...
  if((camera_capture_mode == ONESHOT) & camera_trigger){
    send_image(fb->width, fb->height, fb->format, fb->buf, fb->len);
    camera_trigger = false;
  }
  //...
  if(camera_capture_mode == STREAM){
    send_image(fb->width, fb->height, fb->format, fb->buf, fb->len);
  }
  //...
  esp_camera_fb_return(fb);
}
