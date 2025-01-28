//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef TRACKER_H
#define TRACKER_H

//-----------------------------------------------------------------------------
#include <Arduino.h>
#include "esp_camera.h"
#include "config.h"

#define TRACKER_WIDTH 240
#define TRACKER_HEIGHT 176
#define TRACKER_BUF_LEN TRACKER_WIDTH*TRACKER_HEIGHT

#define TRACKER_FILTER_MIN config.tracker_filter_low
#define TRACKER_ERODE config.tracker_erode
#define TRACKER_ERODE_RATIO config.tracker_erode_mul
#define TRACKER_ERODE_RATIO_DIV config.tracker_erode_div
#define TRACKER_DILATE config.tracker_dilate

//-----------------------------------------------------------------------------
struct point_rect_t{
    size_t x1;
    size_t y1;
    size_t x2;
    size_t y2;
};
enum tracker_status_e{
    WAIT,
    PROCESS,
    READY,
};

extern uint8_t request_frame;
extern tracker_status_e tracker_status;
extern uint8_t tracker_wait_buffer;
extern uint8_t* tracker_buffer_A;
//extern uint8_t* tracker_buffer_B;
extern uint64_t tracker_frame_count;
extern uint8_t tracker_points_len;
extern point_rect_t tracker_points_rect[254];

//-----------------------------------------------------------------------------
void tracker_init();
void tracker_task();
void tracker_render_frame(size_t w, size_t h, pixformat_t pfmt, uint8_t *buf, size_t len);
void push_camera_buffer(camera_fb_t *fb);

//-----------------------------------------------------------------------------
#endif