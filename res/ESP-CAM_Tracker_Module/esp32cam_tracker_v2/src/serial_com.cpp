//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "serial_com.h"
#include "camera.h"
#include "tracker.h"
#include "utils.h"

uint64_t checksum = 0;

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
        send_slip_single(tx_package_type_e::FRAME);
        send_slip_single(TRACKER_WIDTH);
        send_slip_single(TRACKER_HEIGHT);
        send_slip(tracker_buffer_A, TRACKER_BUF_LEN);
        end_slip();
      break;
      //...
      case CMD_REQUEST_RECTS:
        send_slip_single(tx_package_type_e::RECTS);
        send_slip((uint8_t*)tracker_points_rect, tracker_points_len*sizeof(point_rect_t));
        end_slip();
      break;
      //...
      case CMD_REQUEST_FRAME_COUNT:
        send_slip_single(tx_package_type_e::UINTS);
        convert64_u frm_cnt;
        frm_cnt.number = tracker_frame_count;
        send_slip(frm_cnt.div4, 4);
        end_slip();
      break;
    }
  }
}

//-----------------------------------------------------------------------------
void send_slip(uint8_t *buf, size_t len){
  for(size_t i = 0; i < len; i++){
    send_slip_single(buf[i]);
  }
}

//-----------------------------------------------------------------------------
void send_slip_single(uint8_t data){
  checksum += data;
  if(data == S_END){
    Serial.write(S_ESC);
    Serial.write(S_ESC_END);
  }
  else if(data == S_ESC){
    Serial.write(S_ESC);
    Serial.write(S_ESC_ESC);
  }
  else{
    Serial.write(data);
  }
}
//-----------------------------------------------------------------------------
void end_slip(){
  convert64_u value{
    .number = checksum
  };
  send_slip(value.div4, 4);
  Serial.write(S_END);
  checksum = 0;
}

//-----------------------------------------------------------------------------
void send_image(size_t w, size_t h, pixformat_t pfmt, uint8_t *buf, size_t len){
  send_slip_single(tx_package_type_e::FRAME);
  convert64_u w_c{.number=w};
  convert64_u h_c{.number=h};
  send_slip(w_c.div4, 4);
  send_slip(h_c.div4, 4);
  send_slip(buf, len);
  end_slip();
}
