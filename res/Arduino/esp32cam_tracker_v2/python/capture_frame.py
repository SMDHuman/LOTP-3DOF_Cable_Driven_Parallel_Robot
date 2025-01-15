from serial import Serial
import time
import pygame as pg
import numpy as np
import struct
from random import randint
#------------------------------------------------------------------------------
# Constants
S_END = 0xC0
S_ESC = 0xDB
S_ESC_END = 0xDC
S_ESC_ESC = 0xDD
CMD_TRIGGER = 0x0A
CMD_ONESHOT = 0x0B
CMD_STREAM = 0x0C
CMD_ONLED = 0x0D
CMD_REQUEST_FRAME = 0x0E
CMD_REQUEST_RECT = 0x0F
CMD_REQUEST_FRAME_COUNT = 0x10
colors = [(randint(0, 255), randint(0, 255), randint(0, 255)) for i in range(256)]
colors[0] = (0, 0, 0)
#------------------------------------------------------------------------------
keys_pressed = set()
def handle_events():
    global running, keys_pressed
    keys_pressed.clear()
    for event in pg.event.get():
        if(event.type == pg.QUIT):
            running = False
        if(event.type == pg.KEYDOWN):
            keys_pressed.add(event.key)
#------------------------------------------------------------------------------
def read_slip() -> list[int]:
    while((int(esp.read(1)[0]) != S_END)):
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
#------------------------------------------------------------------------------
def frame_process_dif_surf(frame_surf_A: pg.Surface, frame_surf_B: pg.Surface) -> pg.Surface:
    frame_new_surf = pg.Surface(frame_surf_A.get_size())
    for y in range(frame_new_surf.get_height()):
        for x in range(frame_new_surf.get_width()):
            color_A = frame_surf_A.get_at((x, y))
            color_B = frame_surf_B.get_at((x, y))
            gray_A = (color_A[0] + color_A[1] + color_A[2])//3
            gray_B = (color_B[0] + color_B[1] + color_B[2])//3
            diff = gray_A - gray_B
            r = max(diff, 0)
            b = -min(diff, 0)
            r = r if r > 100 else 0
            b = b if b > 100 else 0
            frame_new_surf.set_at((x, y), [max(min(r, 255), 0), 0, max(min(b, 255), 0)])
    return(frame_new_surf)
def frame_jpg_bytes_to_surf(buffer) -> pg.Surface:
    file = open("frame.jpeg", "wb")
    file.write(bytes(buffer))
    file.close()
    #...
    return(pg.image.load("frame.jpeg"))
#------------------------------------------------------------------------------
#...
esp = Serial("COM17", 115200, timeout=1)
esp.read_until(bytes([S_END, S_END])) # If package incoming, wait for the end-start
esp.read_until(bytes([S_END])) # Skip that second package too
pg.init()
win = pg.display.set_mode((800, 600))
clock = pg.time.Clock()
#...
esp.write(bytes([CMD_ONESHOT]))
running = True
font = pg.font.SysFont("arial", 10)
last_frame_count = time.time()
old_frame_count = 0
#------------------------------------------------------------------------------
while(True):
    #...
    handle_events()
    if(not running):
        pg.quit()
        esp.close()
        break
    if(time.time() - last_frame_count >= 1):
        esp.write(bytes([CMD_REQUEST_FRAME_COUNT]))
        frame_count = struct.unpack("I", bytearray(read_slip()))[0]
        print(frame_count - old_frame_count)
        old_frame_count = frame_count
        last_frame_count = time.time()
    #...
    if(pg.K_SPACE in keys_pressed or 1):
        esp.write(bytes([CMD_REQUEST_RECT]))
        rects_package = read_slip()
        #esp.write(bytes([CMD_REQUEST_FRAME]))
        #frame_package = read_slip()
        #print(f"package size: {len(frame_package)}b")
        frame_surf = pg.Surface((240, 176))
        #if(frame_surf.get_width() * frame_surf.get_height() == len(frame_package)-2):
        #    for y in range(frame_surf.get_height()):
        #        for x in range(frame_surf.get_width()):
        #            i = (y*frame_surf.get_width())+x
        #            value = frame_package[i+2]
        #            #print(value, end = ", ") 
        #            c = colors[value]
        #            frame_surf.set_at((x, y), colors[value])
            #print()
        #...
        l = len(rects_package)//16
        for i in range(l-1):
            data = struct.unpack("IIII", bytearray(rects_package[i*16:(i+1)*16]))
            rect = [data[0], data[1], data[2] - data[0]+1, data[3] - data[1]+1]
            #print(data)
            pg.draw.rect(frame_surf, "red", rect, 1)
        #...
        win.blit(pg.transform.scale(frame_surf, win.get_size()), (0, 0))

    #...
    pg.display.update() 
    #print("FPS:", round(clock.get_fps(), 1))
    clock.tick(5)
#------------------------------------------------------------------------------
