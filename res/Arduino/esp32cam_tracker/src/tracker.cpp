//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "tracker.h"
#include "camera.h"
#include "beacon_com.h"

size_t tracker_width = 80;
size_t tracker_height = 60;
static uint16_t tracker_frame_buf[10000];
static uint16_t tracker_old_frame_buf[10000];
uint16_t* tracker_frame;
uint16_t* tracker_old_frame;
uint64_t tracker_frame_count = 0;

//-----------------------------------------------------------------------------
void tracker_init(){
  //tracker_frame = (uint16_t *)malloc(tracker_width * tracker_height * sizeof(uint16_t));
  //tracker_old_frame = (uint16_t *)malloc(tracker_width * tracker_height * sizeof(uint16_t));
  tracker_frame = tracker_frame_buf;
  tracker_old_frame = tracker_old_frame_buf;
}

//-----------------------------------------------------------------------------
void tracker_task(){

}

//-----------------------------------------------------------------------------
void tracker_render_frame(size_t w, size_t h, pixformat_t pfmt, uint8_t *buf, size_t len){
  // Swap pointers
  if(tracker_frame_count % 2 == 0){
    tracker_frame = tracker_frame_buf;
    tracker_old_frame = tracker_old_frame_buf;
  }else{
    tracker_frame = tracker_old_frame_buf;
    tracker_old_frame = tracker_frame_buf;
  }
  //...
  for(size_t i = 0; i < tracker_width*tracker_height; i++){
    tracker_frame[i] = 0;
  }
  //...
  for(size_t y = 0; y < h; y++){
    for(size_t x = 0; x < w; x++){
      uint8_t p_value = buf[(y*w) + x];
      size_t fx = (x*tracker_width)/w;
      size_t fy = (y*tracker_height)/h;
      size_t fi = (fy*tracker_width) + fx;
      if(tracker_frame[fi] + p_value > 0xFFFF){
        tracker_frame[fi] = 0xFFFF;
      }
      else{
        tracker_frame[fi] += p_value;
      }
      //tracker_frame[fi] = 0;
    }
  }
  tracker_frame_count ++;
}
