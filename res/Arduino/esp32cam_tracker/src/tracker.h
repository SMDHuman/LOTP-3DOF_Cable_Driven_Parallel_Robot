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

extern uint8_t tracker_points_len;
extern uint8_t tracker_points_id[16];
extern uint8_t tracker_points_status[16];
extern uint8_t tracker_points_status_old[16];
extern size_t tracker_points[16];

//-----------------------------------------------------------------------------
void tracker_init(size_t w, size_t h);
void tracker_init();
void tracker_task();
void tracker_render_frame(size_t w, size_t h, pixformat_t pfmt, uint8_t *buf, size_t len);
static void tracker_search_frame_diff();

//-----------------------------------------------------------------------------
#endif