import camera, sys
from machine import UART
import time

class ESPcam:
    #...
    def __init__(self):
        #...
        camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
        camera.framesize(camera.FRAME_240X240)
        camera.quality(5)
        #...
        self.uart = UART(0, 115200)
    #...
    def loop(self):
        if(self.uart.any()):
            print(self.uart.read(1))

#buf = camera.capture()
#print(len(buf)/1000, "Kb")
#file = open("frame.jpeg", "w")
#file.write(buf)
#file.close()

if(__name__ == "__main__"):
    cam = ESPcam()
    while(True):
        cam.loop()
        time.sleep(0.01)

