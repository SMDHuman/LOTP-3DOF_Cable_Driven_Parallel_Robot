//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "slip_decoder.h"
#include "serial_com.h"
#include "utils.h"

uint8_t *slip_package_buffer;
size_t slip_buffer_size;
size_t slip_buffer_index;
uint8_t slip_package_ready; 

static uint64_t checksum = 0;

//-----------------------------------------------------------------------------
void slip_init(size_t buffer_size){
    slip_package_buffer = (uint8_t*)malloc(buffer_size);
    slip_buffer_size = buffer_size;
}
//-----------------------------------------------------------------------------
void slip_task(){

}
//-----------------------------------------------------------------------------
void slip_push(uint8_t data){
    static uint8_t esc_flag = false;
    if(slip_package_ready){
        slip_reset();
    }
    if(esc_flag){
        if(data == S_ESC_END){
            slip_package_buffer[slip_buffer_index++] = S_END;
            checksum += S_END;
        }
        else if(data == S_ESC_ESC){
            slip_package_buffer[slip_buffer_index++] = S_ESC;
            checksum += S_ESC;
        }
        esc_flag = false;
    }
    else if(data == S_ESC){
        esc_flag = true;
    }
    else if(data == S_END){
        slip_package_ready = true;
    }
    else{
        slip_package_buffer[slip_buffer_index++] = data;
        checksum += data;
    }
}
//-----------------------------------------------------------------------------
uint8_t slip_is_ready(){
    if(slip_package_ready){
        size_t chsm = 0;
        //Serial.print("checksum div: ");
        for(size_t i = 0; i < 4; i++){
            size_t d = slip_package_buffer[i+slip_buffer_index-4];
            checksum -= d;
            chsm += (d << (i*8));
            //send_debug(slip_package_buffer[i+slip_buffer_index-4]);
        }
        //send_debug(chsm);
        //send_debug(checksum);
        if(checksum == chsm){
            return(true);
        }else{
            slip_reset();
        }
        return(false);
    }
    return(false);
}

void slip_reset(){
    memset(slip_package_buffer, 0, slip_buffer_size);
    slip_buffer_index = 0;
    slip_package_ready = false;
    checksum = 0;
}