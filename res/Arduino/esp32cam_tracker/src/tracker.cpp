//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "tracker.h"
#include "camera.h"
#include "beacon_com.h"

//#define DEBUG

//-----------------------------------------------------------------------------
size_t tracker_width = 64;
size_t tracker_height = 48;
static uint16_t tracker_frame_buf[0x4000];
static uint16_t tracker_old_frame_buf[0x4000];
uint16_t* tracker_frame;
uint16_t* tracker_old_frame;
uint64_t tracker_frame_count = 0;

uint8_t tracker_points_len = 0;
uint8_t tracker_points_id[16];
uint8_t tracker_points_status[16];
uint8_t tracker_points_status_old[16];
size_t tracker_points[16];

//-----------------------------------------------------------------------------
void tracker_init(size_t w, size_t h){
  tracker_width = w;
  tracker_height = h;
  tracker_init();
}
void tracker_init(){
  if(sizeof(tracker_frame_buf)>>1 < tracker_width*tracker_height){
    Serial.println("Not enough memory for Tracker!");
    while(1){}
  }
  //tracker_frame = (uint16_t *)malloc(tracker_width * tracker_height * sizeof(uint16_t));
  //tracker_old_frame = (uint16_t *)malloc(tracker_width * tracker_height * sizeof(uint16_t));
  tracker_frame = tracker_frame_buf;
  tracker_old_frame = tracker_old_frame_buf;
}

//-----------------------------------------------------------------------------
void tracker_task(){
  if(tracker_frame_count >= 2){
    tracker_search_frame_diff();
  }
}

//-----------------------------------------------------------------------------
void tracker_render_frame(size_t w, size_t h, 
                          pixformat_t pfmt, uint8_t *buf, size_t len){
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

//-----------------------------------------------------------------------------
static void tracker_search_frame_diff(){
  int32_t max_diff, min_diff;
  size_t max_diff_i, min_diff_i; 
  for(size_t y = 0; y < tracker_height; y++){
    for(size_t x = 0; x < tracker_width; x++){
      size_t fi = (y*tracker_width) + x;
      int32_t diff = tracker_frame[fi] - tracker_old_frame[fi];
      if(diff > max_diff){
        max_diff = diff;
        max_diff_i = fi;
      }
      if(diff < min_diff){
        min_diff = diff;
        min_diff_i = fi;
      }
    }
  }
  // Makes guess on points position
  for(uint8_t i =0; i < tracker_points_len; i++){
    // Now on, before off
    if(tracker_points_status[i] & !tracker_points_status_old[i]){
      tracker_points[i] = max_diff_i;
    }
    // Now off, before off
    if(!tracker_points_status[i] & tracker_points_status_old[i]){
      tracker_points[i] = min_diff_i;
    }
  }
  #ifdef DEBUG
  for(uint8_t i =0; i < tracker_points_len; i++){
    Serial.print("Point "); Serial.print(i); Serial.print(" At: ");
    Serial.print("x: "); Serial.print(tracker_points[i]%tracker_width);
    Serial.print(", y: "); Serial.println(tracker_points[i]/tracker_width);
  }
  #endif
}