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

#define CMD_TRIGGER 0x0A
#define CMD_ONESHOT 0x0B
#define CMD_STREAM 0x0C
#define CMD_ONLED 0x0D
#define RQT_FRAME 0x0E
#define RQT_RECTS 0x0F
#define RQT_FRAME_COUNT 0x10
#define RQT_T_FRAME_SIZE 0x11
#define RQT_C_FRAME_SIZE 0x12
#define RQT_TRACKER_FRAME 0x13
#define WRITE_CONFIG 0x14
#define READ_CONFIG 0x15

enum tx_package_type_e{
    FRAME,
    RECTS,
    FRAMEC,
    T_SIZE, // Tracker Frame Size
    C_SIZE  // Camera Frame Size
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
