//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef CONFIG_H
#define CONFIG_H
#include <Arduino.h>
//-----------------------------------------------------------------------------
extern struct config_t{
    uint8_t config_restore_default = false;
    int8_t camera_brightness = 0;     // -2 to 2
    int8_t camera_contrast = 0;       // -2 to 2
    int8_t camera_saturation = 0;     // -2 to 2
    uint8_t camera_special_effect = 2;// 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale, 3 - Red Tint, 4 - Green Tint, 5 - Blue Tint, 6 - Sepia)
    uint8_t camera_whitebal = 1;      // 0 = disable , 1 = enable
    uint8_t camera_awb_gain = 1;      // 0 = disable , 1 = enable
    uint8_t camera_wb_mode = 0;       // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
    uint8_t camera_exposure_ctrl = 1; // 0 = disable , 1 = enable
    uint8_t camera_aec2 = 0;          // 0 = disable , 1 = enable
    int8_t camera_ae_level = 0;       // -2 to 2
    uint16_t led_blink_delay = 250;
    uint8_t tracker_filter_low = 235;
    uint8_t tracker_erode = 1;
    uint8_t tracker_erode_mul = 3;
    uint8_t tracker_erode_div = 10;
    uint8_t tracker_dilate = 5;
    uint16_t serial_tx_package_size = 1024;
    uint32_t serial_baudrate = 921600;
} config;

//-----------------------------------------------------------------------------
void config_init();
void config_task();
void config_commit();
void config_set_reset_flag();

//-----------------------------------------------------------------------------
#endif