//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef CAMERA_H
#define CAMERA_H
#include <Arduino.h>
#include "esp_camera.h"

//-----------------------------------------------------------------------------
static camera_config_t camera_config = {
    .pin_pwdn       = 32,
    .pin_reset      = -1,
    .pin_xclk       = 0,
    .pin_sccb_sda   = 26,
    .pin_sccb_scl   = 27,
    .pin_d7         = 35,
    .pin_d6         = 34,
    .pin_d5         = 39,
    .pin_d4         = 36,
    .pin_d3         = 21,
    .pin_d2         = 19,
    .pin_d1         = 18,
    .pin_d0         = 5,
    .pin_vsync      = 25,
    .pin_href       = 23,
    .pin_pclk       = 22,

    .xclk_freq_hz   = 20000000,
    .ledc_timer     = LEDC_TIMER_0,
    .ledc_channel   = LEDC_CHANNEL_0,
    .pixel_format   = PIXFORMAT_GRAYSCALE,
    .frame_size     = FRAMESIZE_HQVGA,
    .jpeg_quality   = 10,
    .fb_count       = 2,
    .fb_location    = CAMERA_FB_IN_PSRAM,
    .grab_mode      = CAMERA_GRAB_LATEST
};

//-----------------------------------------------------------------------------
enum capture_mode_e {
    ONESHOT,
    STREAM,
    ONLED
};
extern capture_mode_e camera_capture_mode;
extern bool camera_trigger;
extern uint64_t camera_width;
extern uint64_t camera_height;

//-----------------------------------------------------------------------------
void camera_init();
void camera_task();

//-----------------------------------------------------------------------------
#endif
