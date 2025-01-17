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
    //...
    camera_trigger = false;
    switch(cmd){
      //...
      case CMD_TRIGGER:
        if(camera_capture_mode == ONESHOT){
          camera_trigger = true;
        }
      break;
      //...
      case CMD_ONESHOT:
        camera_capture_mode = ONESHOT;
      break;
      //...
      case CMD_STREAM:
        camera_capture_mode = STREAM;
      break;
      //...
      case CMD_ONLED:
        camera_capture_mode = ONLED;
      break;
      //...
      case CMD_REQUEST_FRAME:
        end_slip();
        send_slip((uint8_t *)tracker_frame, tracker_width*tracker_height*2);
        end_slip();
      break;
      //...
      case CMD_REQUEST_POINTS:
        end_slip();
        send_slip(tracker_points_id, sizeof(tracker_points_id));
        send_slip((uint8_t*)tracker_points, sizeof(tracker_points));
        end_slip();
      break;
    }
  }
}

//-----------------------------------------------------------------------------
void send_slip(uint8_t *buf, size_t len){
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
}
//-----------------------------------------------------------------------------
void end_slip(){
  Serial.write(S_END);
}

//-----------------------------------------------------------------------------
void send_image(size_t w, size_t h, pixformat_t pfmt, uint8_t *buf, size_t len){
 end_slip();
 send_slip(buf, len);
 end_slip();
}
