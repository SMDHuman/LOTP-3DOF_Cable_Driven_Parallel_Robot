//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#ifndef SLIP_DECODER_H
#define SLIP_DECODER_H

//-----------------------------------------------------------------------------
#include <Arduino.h>

#define S_END 0xC0
#define S_ESC 0xDB
#define S_ESC_END 0xDC
#define S_ESC_ESC 0xDD

//-----------------------------------------------------------------------------
extern uint8_t *slip_package_buffer;
extern size_t slip_buffer_size;
extern size_t slip_buffer_index;
extern uint8_t slip_package_ready; 

//-----------------------------------------------------------------------------
void slip_init(size_t buffer_size = 2048);
void slip_task();
void slip_push(uint8_t data);
uint8_t slip_is_ready();
void slip_reset();

//-----------------------------------------------------------------------------
#endif