//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef SERIAL_COM_H
#define SERIAL_COM_H
#include <Arduino.h>
#include "esp_camera.h"
#include "config.h"

//-----------------------------------------------------------------------------
#define BAUDRATE config.serial_baudrate
#define S_MAX_PACKAGE config.serial_tx_package_size

//-----------------------------------------------------------------------------
enum rx_package_type_e{
    CMD_TRIGGER = 0x0A,
    CMD_ONESHOT,
    CMD_STREAM,
    CMD_ONLED,
    RQT_FRAME,
    RQT_RECTS,
    RQT_FRAME_COUNT,
    RQT_T_FRAME_SIZE,
    RQT_C_FRAME_SIZE,
    RQT_TRACKER_FRAME,
    WRITE_CONFIG,
    READ_CONFIG,
    RESET_CONFIG
};
enum tx_package_type_e{
    FRAME,        // byte array of requested buffer and size
    RECTS,        // (x1, y1, x2, y2) located bright points
    FRAME_COUNT,  // Processed frame count since boot
    TRACKER_SIZE, // Tracker Frame Size
    CAMERA_SIZE,  // Camera Frame Size
    CONFIG,
    DEBUG_STR,
};

//-----------------------------------------------------------------------------
void serial_init();
void serial_task();
void send_slip(uint8_t *buf, size_t len);
void send_slip_single(uint8_t data);
void send_image(size_t w, size_t h, uint8_t *buf, size_t len, uint8_t id = 0);
void send_debug(String text);
void send_debug(int number);
void end_slip();

//-----------------------------------------------------------------------------
#endif
