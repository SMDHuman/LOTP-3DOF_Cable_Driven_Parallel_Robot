//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "beacon_com.h"
#include "camera.h"
#include "tracker.h"

//#define DEBUG

uint8_t beacon_led_status;
uint64_t beacon_last_msg;
static uint8_t beacon_status_update = 0;

//-----------------------------------------------------------------------------
static void on_data_recv(const uint8_t * mac, const uint8_t *package, int len){
  if(len > 1){
    if(package[0] == 0xC0){
      beacon_status_update = 1;
      if(camera_capture_mode == ONLED){
        camera_trigger = true;
      }
      //...
      int8_t find = -1;
      for(uint8_t i =0; i < tracker_points_len; i++){
        if(tracker_points_id[i] == package[1]){
          find = i;
          break;
        }
      }
      if((find == -1) & tracker_points_len < sizeof(tracker_points_id)){
        tracker_points_id[tracker_points_len] = package[1];
        tracker_points_status[tracker_points_len] = package[2];
        tracker_points_len++;
      }else if(find>=0){
        tracker_points_status_old[find] = tracker_points_status[find];
        tracker_points_status[find] = package[2];
      }
    }
    //...
    #ifdef DEBUG
    for(uint8_t i =0; i < tracker_points_len; i++){
      Serial.print("ID ");Serial.print(i);Serial.print(": ");
      Serial.print(tracker_points_id[i]);
      Serial.print(", Led: ");
      Serial.println(tracker_points_status[i]);
    }
    #endif
  }
}

//-----------------------------------------------------------------------------
void beacon_init(){
  WiFi.mode(WIFI_STA);
  if(esp_now_init() != ESP_OK){
    Serial.println("Error initializing ESPnow");
    return;
  }
  esp_now_register_recv_cb(on_data_recv);
}

//-----------------------------------------------------------------------------
void beacon_task(){

}

//-----------------------------------------------------------------------------
int8_t get_beacon_last_stat(){
  if(beacon_status_update == 1){
    beacon_status_update = 0;
    return(beacon_led_status);
  }
  return(-1);
}