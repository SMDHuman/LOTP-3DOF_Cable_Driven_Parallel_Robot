//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "tracker.h"
#include "camera.h"
#include "beacon_com.h"

//#define DEBUG
//-----------------------------------------------------------------------------
static void switch_buffers();
static void filter_buffer();
static void erode_buffer();
static void dilate_buffer();
static void flood_fill(size_t s_i, uint8_t value);
static void flood_buffer();
static void locate_rect_buffer();

//-----------------------------------------------------------------------------
//...
static uint8_t buffer_A[TRACKER_WIDTH*TRACKER_HEIGHT];
static uint8_t buffer_B[TRACKER_WIDTH*TRACKER_HEIGHT];
uint8_t* tracker_buffer_A = buffer_A;
uint8_t* tracker_buffer_B = buffer_B;
uint64_t tracker_frame_count = 0;
//...
uint8_t tracker_points_len = 0;
point_rect_t tracker_points_rect[254];
tracker_status_e tracker_status = WAIT;

//-----------------------------------------------------------------------------
void tracker_init(){
  //tracker_frame = (uint16_t *)malloc(tracker_width * tracker_height * sizeof(uint16_t));
  //tracker_old_frame = (uint16_t *)malloc(tracker_width * tracker_height * sizeof(uint16_t));
}

//-----------------------------------------------------------------------------
void tracker_task(){
  if(tracker_status == READY){
    tracker_status = PROCESS;
    //...
    switch_buffers();
    filter_buffer();
    //...
    switch_buffers();
    erode_buffer();
    //...
    switch_buffers();
    dilate_buffer();
    //...
    flood_buffer();
    locate_rect_buffer();
    tracker_status = WAIT;
    tracker_frame_count++;
  }
}

//-----------------------------------------------------------------------------
static void switch_buffers(){
  static uint8_t buffer_order = true;
  if(buffer_order){
    tracker_buffer_A = buffer_B;
    tracker_buffer_B = buffer_A;
  }else{
    tracker_buffer_A = buffer_A;
    tracker_buffer_B = buffer_B;
  }
  buffer_order = !buffer_order;
}
//-----------------------------------------------------------------------------
// Pushes camera frame buffer to tracker buffer 'A'
void push_camera_buffer(camera_fb_t *fb){
  switch_buffers();
  for(size_t y = 0; y < TRACKER_HEIGHT; y++){
    for(size_t x = 0; x < TRACKER_WIDTH; x++){
      size_t fb_x = (fb->width * x) / TRACKER_WIDTH;
      size_t fb_y = (fb->height * y) / TRACKER_HEIGHT;
      tracker_buffer_A[(y*TRACKER_WIDTH)+x] = fb->buf[(fb_y*fb->width)+fb_x];
    }
  }
}
//-----------------------------------------------------------------------------
// Apply TRACKER_FILTER_MIN filter from 'B' to 'A' buffer
static void filter_buffer(){
  for(size_t i = 0; i < TRACKER_WIDTH*TRACKER_HEIGHT; i++){
    if(tracker_buffer_B[i] < TRACKER_FILTER_MIN){
      tracker_buffer_A[i] = 0x00;
    }else{
      tracker_buffer_A[i] = 0xFF;
    }
  }
}
//-----------------------------------------------------------------------------
static void erode_buffer(){
  //...
  for(size_t i = 0; i < TRACKER_WIDTH*TRACKER_HEIGHT; i++){
    tracker_buffer_A[i] = 0;
  }
  //...
  static const uint16_t area = (TRACKER_ERODE*2+1)*(TRACKER_ERODE*2+1); 
  for(size_t y = 0; y < TRACKER_HEIGHT-(TRACKER_ERODE*2); y++){
    for(size_t x = 0; x < TRACKER_WIDTH-(TRACKER_ERODE*2); x++){
      //...
      uint16_t count = 0;
      for(size_t dy = 0; dy < TRACKER_ERODE*2+1; dy++){
        for(size_t dx = 0; dx < TRACKER_ERODE*2+1; dx++){
          if(tracker_buffer_B[((y+dy)*TRACKER_WIDTH)+(x+dx)] == 0xFF){
            count ++;
          }
      }}
      if(area*TRACKER_ERODE_RATIO <= count*TRACKER_ERODE_RATIO_DIV){
        tracker_buffer_A[((y+TRACKER_ERODE)*TRACKER_WIDTH)+(x+TRACKER_ERODE)] = 0xFF;
      }else{
        tracker_buffer_A[((y+TRACKER_ERODE)*TRACKER_WIDTH)+(x+TRACKER_ERODE)] = 0x0;
      }
  }}
}
//-----------------------------------------------------------------------------
static void dilate_buffer(){
  //...
  for(size_t i = 0; i < TRACKER_WIDTH*TRACKER_HEIGHT; i++){
    tracker_buffer_A[i] = 0;
  }
  //...
  for(size_t y = 0; y < TRACKER_HEIGHT-(TRACKER_DILATE*2); y++){
    for(size_t x = 0; x < TRACKER_WIDTH-(TRACKER_DILATE*2); x++){
      //...
      if(tracker_buffer_B[((y+TRACKER_DILATE)*TRACKER_WIDTH)+(x+TRACKER_DILATE)] == 0xFF){
        for(size_t dy = 0; dy < TRACKER_DILATE*2+1; dy++){
          for(size_t dx = 0; dx < TRACKER_DILATE*2+1; dx++){
            tracker_buffer_A[((y+dy)*TRACKER_WIDTH)+(x+dx)] = 0xFF;
        }}
      }
  }}
}

//-----------------------------------------------------------------------------
static void flood_buffer(){
  uint8_t island_count = 1;
  for(size_t i = 0; i < TRACKER_WIDTH*TRACKER_HEIGHT; i++){
    if(tracker_buffer_A[i] == 255){
      flood_fill(i, island_count);
      island_count++;
      if(island_count == 255){
        return;
      }
    }
  }
  tracker_points_len = island_count;
}

//-----------------------------------------------------------------------------
static void flood_fill(size_t s_i, uint8_t value) 
{ 
  uint8_t base_value = tracker_buffer_A[s_i];
  size_t check[500] = {s_i};
  uint16_t check_len = 1;
  while(check_len > 0){
    if(check_len > (sizeof(check)>>2)){
      check_len = (sizeof(check)>>2);
    }
    size_t i = check[--check_len];
    // Base cases 
    if ((i < 0) | (i > TRACKER_WIDTH*TRACKER_HEIGHT)) {
      continue; 
    }
    //...
    tracker_buffer_A[i] = value; 
    //...
    if((tracker_buffer_A[i-1] != value) & (tracker_buffer_A[i-1] == base_value)){
      if(check_len < (sizeof(check)>>2)){
        check[check_len++] = i-1;
      }
    }
    if((tracker_buffer_A[i+1] != value) & (tracker_buffer_A[i+1] == base_value)){
      if(check_len < (sizeof(check)>>2)){
        check[check_len++] = i+1;
      }
    }
    if((tracker_buffer_A[i-TRACKER_WIDTH] != value) & (tracker_buffer_A[i-TRACKER_WIDTH] == base_value)){
      if(check_len < (sizeof(check)>>2)){
        check[check_len++] = i-TRACKER_WIDTH;
      }
    }
    if((tracker_buffer_A[i+TRACKER_WIDTH] != value) & (tracker_buffer_A[i+TRACKER_WIDTH] == base_value)){
      if(check_len < (sizeof(check)>>2)){
        check[check_len++] = i+TRACKER_WIDTH;
      }
    }
  }
} 
//-----------------------------------------------------------------------------
static void locate_rect_buffer(){
  for(uint8_t i = 0; i < 254; i++){
    tracker_points_rect[i].x1 = TRACKER_WIDTH;
    tracker_points_rect[i].y1 = TRACKER_HEIGHT;
    tracker_points_rect[i].x2 = 0;
    tracker_points_rect[i].y2 = 0;
  }
  for(size_t y = 0; y < TRACKER_HEIGHT; y++){
    for(size_t x = 0; x < TRACKER_WIDTH; x++){
      size_t i = (y*TRACKER_WIDTH)+x;
      if((tracker_buffer_A[i] > 0) & (tracker_buffer_A[i] < 255)){
        uint8_t ri = tracker_buffer_A[i]-1;
        point_rect_t *rect = &tracker_points_rect[ri];
        if(x < rect->x1){
          rect->x1 = x;
        }
        if(y < rect->y1){
          rect->y1 = y;
        }
        if(x > rect->x2){
          rect->x2 = x;
        }
        if(y > rect->y2){
          rect->y2 = y;
        }
      }
    }
  }
}