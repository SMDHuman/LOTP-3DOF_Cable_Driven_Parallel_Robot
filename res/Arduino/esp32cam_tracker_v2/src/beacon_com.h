//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef BEACON_COM_H
#define BEACON_COM_H

#include <esp_now.h>
#include <Wifi.h>
//-----------------------------------------------------------------------------
extern uint8_t beacon_led_status;
extern uint64_t beacon_last_msg;

//-----------------------------------------------------------------------------
static void on_data_recv(const uint8_t * mac, const uint8_t *incomingData, int len);
void beacon_init();
void beacon_task();
int8_t get_beacon_last_stat();

//-----------------------------------------------------------------------------
#endif