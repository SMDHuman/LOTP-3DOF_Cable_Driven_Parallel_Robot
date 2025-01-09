from serial import Serial
import time
import pygame as pg
import numpy as np
import struct
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
CMD_REQUEST_POINTS = 0x0F
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
esp = Serial("COM3", 115200, timeout=1)
esp.read_until(bytes([S_END, S_END])) # If package incoming, wait for the end-start
esp.read_until(bytes([S_END])) # Skip that second package too
pg.init()
win = pg.display.set_mode((800, 600))
clock = pg.time.Clock()
#...
esp.write(bytes([CMD_ONESHOT]))
frame_frame_surf = pg.Surface((240, 240))
frame_frame_surf_clipped = pg.Surface(frame_frame_surf.get_size())
running = True
font = pg.font.SysFont("arial", 10)
frame_surf = pg.Surface((64, 48))
#------------------------------------------------------------------------------
while(True):
    #...
    handle_events()
    if(not running):
        pg.quit()
        esp.close()
        break
    #...
    if(pg.K_SPACE in keys_pressed):
        esp.write(bytes([CMD_REQUEST_FRAME]))
    if(pg.K_RETURN in keys_pressed):
        esp.write(bytes([CMD_REQUEST_POINTS]))
    # Read and display incoming frame
    if(esp.in_waiting):
        package = read_slip()
        print(f"package size: {len(package)}b")
        if(len(package) >= 3000):
            for y in range(frame_surf.get_height()):
                for x in range(frame_surf.get_width()):
                    i = (y*frame_surf.get_width())+x
                    value = (package[i*2 + 1] << 8) + (package[i*2])
                    #print(value, end = ", ") 
                    c = int(value*255/65535)
                    frame_surf.set_at((x, y),(c, c, c))
                #print()
            win.blit(pg.transform.scale(frame_surf, win.get_size()), (0, 0))
        elif(len(package) > 0):
            data = struct.unpack("16B16L", bytes(package))
            points_id, points = data[:16], data[16:]
            for i, p in zip(points_id, points):
                x, y = p%frame_surf.get_width(), p//frame_surf.get_width()
                text = font.render(f"id:{i}", 0, "red")
                win.blit(text, (x*win.get_width()//frame_surf.get_width(), y*win.get_height()//frame_surf.get_height()))

    #...
    pg.display.update()
    #print("FPS:", round(clock.get_fps(), 1))
    clock.tick()
#------------------------------------------------------------------------------
