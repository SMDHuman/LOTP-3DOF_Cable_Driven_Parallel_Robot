//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "serial_com.h"
#include "camera.h"
#include "tracker.h"

//-----------------------------------------------------------------------------
void serial_init(){
  Serial.begin(BAUDRATE);
}

//-----------------------------------------------------------------------------
void serial_task(){
  if(Serial.available()){
    uint8_t cmd = Serial.read();
    camera_trigger = false;
    if((cmd == CMD_TRIGGER) & (camera_capture_mode == ONESHOT)){
      camera_trigger = true;
    }
    else if(cmd == CMD_ONESHOT){
      camera_capture_mode = ONESHOT;
    }
    else if(cmd == CMD_STREAM){
      camera_capture_mode = STREAM;
    }
    else if(cmd == CMD_ONLED){
      camera_capture_mode = ONLED;
    }
    else if(cmd == CMD_REQUEST_FRAME){
      send_slip((uint8_t *)tracker_frame, tracker_width*tracker_height*2);
    }
  }
}

//-----------------------------------------------------------------------------
void send_slip(uint8_t *buf, size_t len){
  Serial.write(S_END);
  for(size_t i = 0; i < len; i++){
    if(buf[i] == S_END){
      Serial.write(S_ESC);
      Serial.write(S_ESC_END);
    }
    else if(buf[i] == S_ESC){
      Serial.write(S_ESC);
      Serial.write(S_ESC_ESC);
    }
    else{
      Serial.write(buf[i]);
    }
  }
  Serial.write(S_END);
}

//-----------------------------------------------------------------------------
void send_image(size_t w, size_t h, pixformat_t pfmt, uint8_t *buf, size_t len){
  send_slip(buf, len);
}
