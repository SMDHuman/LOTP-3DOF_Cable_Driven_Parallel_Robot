//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef TRACKER_H
#define TRACKER_H

//-----------------------------------------------------------------------------
#include <Arduino.h>
#include "esp_camera.h"

//-----------------------------------------------------------------------------
extern size_t tracker_width;
extern size_t tracker_height;

extern uint16_t* tracker_frame;
extern uint16_t* tracker_old_frame;
extern uint64_t tracker_frame_count;

//-----------------------------------------------------------------------------
void tracker_init();
void tracker_task();
void tracker_render_frame(size_t w, size_t h, pixformat_t pfmt, uint8_t *buf, size_t len);

//-----------------------------------------------------------------------------
#endif