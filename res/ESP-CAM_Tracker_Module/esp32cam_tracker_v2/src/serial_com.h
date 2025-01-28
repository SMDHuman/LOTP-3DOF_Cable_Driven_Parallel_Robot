//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef SERIAL_COM_H
#define SERIAL_COM_H
#include <Arduino.h>
#include "esp_camera.h"
#include "config.h"

//-----------------------------------------------------------------------------
#define BAUDRATE 921600 
#define S_MAX_PACKAGE config.serial_package_size

//-----------------------------------------------------------------------------
#define S_END 0xC0
#define S_ESC 0xDB
#define S_ESC_END 0xDC
#define S_ESC_ESC 0xDD

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
    FRAME,
    RECTS,
    FRAME_COUNT,
    TRACKER_SIZE, // Tracker Frame Size
    CAMERA_SIZE,  // Camera Frame Size
    CONFIG
};

//-----------------------------------------------------------------------------
void serial_init();
void serial_task();
void send_slip(uint8_t *buf, size_t len);
void send_slip_single(uint8_t data);
void send_image(size_t w, size_t h, uint8_t *buf, size_t len, uint8_t id = 0);
void end_slip();

//-----------------------------------------------------------------------------
#endif
