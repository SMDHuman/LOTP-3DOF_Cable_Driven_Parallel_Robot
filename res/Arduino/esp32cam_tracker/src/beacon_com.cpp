//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "beacon_com.h"

//-----------------------------------------------------------------------------
static void on_data_recv(const uint8_t * mac, const uint8_t *incomingData, int len){
    for(int32_t i = 0; i < len; i++){
        Serial.write(incomingData[i]);
    }
    Serial.println();
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
