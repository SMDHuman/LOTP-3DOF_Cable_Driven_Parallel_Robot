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