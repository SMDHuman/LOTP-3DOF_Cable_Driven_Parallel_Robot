from serial import Serial
import time
from PIL import Image
import pygame as pg
import numpy as np
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
def get_frame() -> list[int]:
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
def process_dif_surf(surf_A: pg.Surface, surf_B: pg.Surface) -> pg.Surface:
    new_surf = pg.Surface(surf_A.get_size())
    for y in range(new_surf.get_height()):
        for x in range(new_surf.get_width()):
            color_A = surf_A.get_at((x, y))
            color_B = surf_B.get_at((x, y))
            gray_A = (color_A[0] + color_A[1] + color_A[2])//3
            gray_B = (color_B[0] + color_B[1] + color_B[2])//3
            diff = gray_A - gray_B
            r = max(diff, 0)
            b = -min(diff, 0)
            r = r if r > 100 else 0
            b = b if b > 100 else 0
            new_surf.set_at((x, y), [max(min(r, 255), 0), 0, max(min(b, 255), 0)])
    return(new_surf)
def jpg_bytes_to_surf(buffer) -> pg.Surface:
    file = open("frame.jpeg", "wb")
    file.write(bytes(buffer))
    file.close()
    #...
    return(pg.image.load("frame.jpeg"))
#------------------------------------------------------------------------------
#...
capture_mode = CMD_STREAM
esp = Serial("COM3", 115200, timeout=1)
esp.read_until(bytes([S_END, S_END])) # If package incoming, wait for the end-start
esp.read_until(bytes([S_END])) # Skip that second package too
pg.init()
win = pg.display.set_mode((480, 480))
clock = pg.time.Clock()
#...
esp.write(bytes([capture_mode]))
frame_surf = pg.Surface((240, 240))
frame_surf_clipped = pg.Surface(frame_surf.get_size())
running = True
#------------------------------------------------------------------------------
while(True):
    #...
    handle_events()
    if(not running):
        pg.quit()
        esp.close()
        break
    # Read and display incoming frame
    if(esp.in_waiting):
        frame = get_frame()
        print(f"frame size: {len(frame)}b")
        if(len(frame) > 0):
            #...
            frame_surf_old = frame_surf
            frame_surf = jpg_bytes_to_surf(frame)
            #...
            frame_surf_clipped_old = frame_surf_clipped
            frame_surf_clipped = pg.Surface(frame_surf.get_size())
            frame_surf_clipped.fill("white")
            pg.transform.threshold(frame_surf_clipped, frame_surf, (255, 255, 255, 255), (100 ,100 ,100, 255))
            #...
            dif_frame_surf = process_dif_surf(frame_surf_clipped, frame_surf_clipped_old)
            #...
            win.blit(frame_surf, (0, 0))
            win.blit(frame_surf_old, (240, 0))
            win.blit(frame_surf_clipped, (0, 240))
            win.blit(dif_frame_surf, (240, 240))
    #...
    pg.display.update()
    #print("FPS:", round(clock.get_fps(), 1))
    clock.tick()
#------------------------------------------------------------------------------
