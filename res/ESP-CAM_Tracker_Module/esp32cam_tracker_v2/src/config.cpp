//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
#include "config.h"
#include <EEPROM.h>
//-----------------------------------------------------------------------------

config_t config;

//-----------------------------------------------------------------------------
void config_init(){
    EEPROM.begin(512);
    //Restore Default
    if(EEPROM.readByte(0) != 0){
        config_commit();
    }else{
        EEPROM.get(0, config);
    }
}
//-----------------------------------------------------------------------------
void config_task(){

}
//-----------------------------------------------------------------------------
// Saves the current variables of config to NVS
void config_commit(){
    EEPROM.put(0, config);
    EEPROM.commit();
}
//-----------------------------------------------------------------------------
// Set the default config flag to 1. Module will restore the default configs on the next boot
void config_set_reset_flag(){
    EEPROM.writeByte(0, 0x01);
    EEPROM.commit();
}