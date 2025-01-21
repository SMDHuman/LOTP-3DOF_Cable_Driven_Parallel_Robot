//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef SERIAL_COM_H
#define SERIAL_COM_H
#include <Arduino.h>
#include "esp_camera.h"

//-----------------------------------------------------------------------------
#define BAUDRATE 115200

//-----------------------------------------------------------------------------
#define S_END 0xC0
#define S_ESC 0xDB
#define S_ESC_END 0xDC
#define S_ESC_ESC 0xDD

#define CMD_TRIGGER 0x0A
#define CMD_ONESHOT 0x0B
#define CMD_STREAM 0x0C
#define CMD_ONLED 0x0D
#define CMD_REQUEST_FRAME 0x0E
#define CMD_REQUEST_RECTS 0x0F
#define CMD_REQUEST_FRAME_COUNT 0x10

enum tx_package_type_e{
    FRAME,
    RECTS,
    UINTS,
    INTS
};

//-----------------------------------------------------------------------------
void serial_init();
void serial_task();
void send_slip(uint8_t *buf, size_t len);
void send_slip_single(uint8_t data);
void send_image(size_t w, size_t h, pixformat_t pfmt, uint8_t *buf, size_t len);
void end_slip();

//-----------------------------------------------------------------------------
#endif
