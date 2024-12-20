//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "camera.h"
#include "serial_com.h"
//-----------------------------------------------------------------------------
capture_mode_e camera_capture_mode = ONESHOT;
bool camera_trigger;

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
  if((camera_capture_mode == ONESHOT) & camera_trigger){
    camera_fb_t *fb = esp_camera_fb_get();
    if(fb){
      send_image(fb->width, fb->height, fb->format, fb->buf, fb->len);
      esp_camera_fb_return(fb);
      camera_trigger = false;
    }
    esp_camera_fb_return(fb);
  }
  if(camera_capture_mode == STREAM){
      camera_fb_t *fb = esp_camera_fb_get();
      if(fb){
        send_image(fb->width, fb->height, fb->format, fb->buf, fb->len);
      }
      esp_camera_fb_return(fb);
  }
}