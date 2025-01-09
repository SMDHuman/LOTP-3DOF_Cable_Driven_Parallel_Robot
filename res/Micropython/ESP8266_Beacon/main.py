import network
import espnow
import time
from machine import Pin

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
bcast = b'\xff\xff\xff\xff\xff\xff'   # MAC address of peer's wifi interface

led = Pin(2, Pin.OUT)
button = Pin(0, Pin.IN)
led_value = 0
while(True):
    while(button.value()): pass
    led.value(led_value)
    time.sleep(1/5)
    # [header, device id, led status]
    e.send(bcast, bytes([0xC0, 0x01, led_value]))
    led_value = not led_value