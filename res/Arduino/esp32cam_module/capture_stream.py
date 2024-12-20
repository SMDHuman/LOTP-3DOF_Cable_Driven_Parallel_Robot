from serial import Serial
import time
from PIL import Image
import pygame as pg

# Constants
S_END = 0xC0
S_ESC = 0xDB
S_ESC_END = 0xDC
S_ESC_ESC = 0xDD
CMD_TRIGGER = 0x0A
CMD_ONESHOT = 0x0B
CMD_STREAM = 0x0C

keys_pressed = set()
def handle_events():
    global running, keys_pressed
    keys_pressed.clear()
    for event in pg.event.get():
        if(event.type == pg.QUIT):
            running = False
        if(event.type == pg.KEYDOWN):
            keys_pressed.add(event.key)

def get_frame(wait_end = True) -> list[int]:
    while((int(esp.read(1)[0]) != S_END) and wait_end):
        pass
    data_buf = esp.read_until(bytes([S_END]))
    frame_buf: list[int] = []
    i = 0
    while(i < len(data_buf)):
        data = int(data_buf[i])
        i += 1
        if(data == S_ESC):
            data_esc = int(data_buf[i])
            i += 1
            if(data_esc == S_ESC_END):
                frame_buf.append(S_END)
            elif(data_esc == S_ESC_ESC):
                frame_buf.append(S_ESC)
        elif(data == S_END):
            break
        else:
            frame_buf.append(data)
    #...
    return(frame_buf)

#...
esp = Serial("COM17", 115200)
pg.init()
win = pg.display.set_mode((480, 480))
clock = pg.time.Clock()

capture_mode = "STREAM"
esp.write(bytes([CMD_STREAM]))
frame_surf = pg.Surface(win.get_size())
running = True
while(True):
    #...
    handle_events()
    if(not running):
        pg.quit()
        esp.close()
        break
    # Change mode on SPACE
    if(32 in keys_pressed):
        if(capture_mode == "STREAM"):
            esp.write(bytes([CMD_ONESHOT]))
            capture_mode = "ONESHOT"
        elif(capture_mode == "ONESHOT"):
            esp.write(bytes([CMD_STREAM]))
            capture_mode = "STREAM"
    #...
    if(capture_mode == "STREAM"):
        frame = get_frame()
        print(len(frame))
        #...
        file = open("frame.jpeg", "wb")
        file.write(bytes(frame))
        file.close()
        #...
        frame_surf = pg.transform.scale(pg.image.load("frame.jpeg"), win.get_size())
    elif(capture_mode == "ONESHOT"):
        if(13 in keys_pressed):
            esp.write(bytes([CMD_TRIGGER]))
            frame = get_frame(False)
            print(len(frame))
            #...
            file = open("frame.jpeg", "wb")
            file.write(bytes(frame))
            file.close()
            #...
            frame_surf = pg.transform.scale(pg.image.load("frame.jpeg"), win.get_size())

    win.blit(frame_surf, (0, 0))

    pg.display.update()
    #print(clock.get_fps())
    clock.tick()