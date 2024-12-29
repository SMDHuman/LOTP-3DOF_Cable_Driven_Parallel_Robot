//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "beacon_com.h"
#include "camera.h"

//-----------------------------------------------------------------------------
static void on_data_recv(const uint8_t * mac, const uint8_t *package, int len){
  if(len > 1){
    if(package[0] == 0xC0){
      camera_trigger = true;
    }
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
