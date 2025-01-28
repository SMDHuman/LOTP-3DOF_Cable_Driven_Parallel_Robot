//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "serial_com.h"
#include "camera.h"
#include "tracker.h"
#include "utils.h"

uint64_t checksum = 0;
uint64_t data_count = 0;
uint8_t wait_ack = false;

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
      case RQT_FRAME:
        send_slip_single(FRAME);
        send_slip_single(TRACKER_WIDTH);
        send_slip_single(TRACKER_HEIGHT);
        send_slip(tracker_buffer_A, TRACKER_BUF_LEN);
        end_slip();
      break;
      //...
      case RQT_RECTS:
        send_slip_single(RECTS);
        send_slip((uint8_t*)tracker_points_rect, tracker_points_len*sizeof(point_rect_t));
        end_slip();
      break;
      //...
      case RQT_FRAME_COUNT:
      {
        send_slip_single(FRAME_COUNT);
        convert64_u frm_cnt{.number=tracker_frame_count};
        send_slip(frm_cnt.div4, 4);
        end_slip();
      }
      break;
      //...
      case RQT_T_FRAME_SIZE:
        send_slip_single(TRACKER_SIZE);
        send_slip_single(TRACKER_WIDTH);
        send_slip_single(TRACKER_HEIGHT);
        end_slip();
      break;
      //...
      case RQT_C_FRAME_SIZE:
      {
        send_slip_single(CAMERA_SIZE);
        convert64_u cw{.number=camera_width};
        send_slip(cw.div4, 4);
        convert64_u ch{.number=camera_height};
        send_slip(ch.div4, 4);
        end_slip();
      }
      break;
      case RQT_TRACKER_FRAME:
      {
        uint8_t section = Serial.read();
        request_frame = section;
      }
      break;
      case WRITE_CONFIG:
      {
        //...
        uint8_t config_package[sizeof(config)];
        Serial.read(config_package, sizeof(config));
        //...
        memcpy(&config, config_package, sizeof(config));
        config_commit();
      }
      break;
      case READ_CONFIG:
      {
        send_slip_single(CONFIG);
        uint8_t config_package[sizeof(config)];
        memcpy(config_package, &config, sizeof(config));
        send_slip(config_package, sizeof(config));
        end_slip();
      }
      break;
      case RESET_CONFIG:
      {
        config_set_reset_flag();
      }
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
  if(data_count == S_MAX_PACKAGE){
    Serial.write(S_ESC); // ESC+END == ACK
    Serial.write(S_END);
    while(!Serial.available()); // Wair for ACK
    Serial.read();
    data_count = 0;
  }
  //...
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
  data_count++;
}
//-----------------------------------------------------------------------------
void end_slip(){
  convert64_u value{
    .number = checksum
  };
  send_slip(value.div4, 4);
  Serial.write(S_END);
  checksum = 0;
  data_count = 0;
}

//-----------------------------------------------------------------------------
void send_image(size_t w, size_t h, uint8_t *buf, size_t len, uint8_t id){
  send_slip_single(tx_package_type_e::FRAME);
  send_slip_single(id);
  convert64_u w_c{.number=w};
  convert64_u h_c{.number=h};
  send_slip(w_c.div4, 4); // Send width
  send_slip(h_c.div4, 4); // Send height
  send_slip(buf, len);    // Frame buffer
  end_slip();
}
