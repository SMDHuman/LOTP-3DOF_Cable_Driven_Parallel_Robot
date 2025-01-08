from serial import Serial
import time
from PIL import Image
import pygame as pg
import numpy as np
import math
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
def collapse_target_color(surf: pg.Surface, target_color, distance:float, div:tuple[int, int], size:tuple[int, int]) -> tuple[list[float], int, int]:
    out_width: int = div[0]
    out_height: int = div[1]
    output: list[float] = [.0]*out_width*out_height
    #../
    for y in range(surf.get_height()):
        for x in range(surf.get_width()):
            color = surf.get_at((x, y))
            color_diff = [target_color[i] - color[i] for i in range(3)]
            diff_mag = math.sqrt(sum([cd**2 for cd in color_diff]))
            if(diff_mag > distance):
                continue
            value = diff_mag
            #...
            d2w:float = surf.get_width()/div[0]
            d2h:float = surf.get_height()/div[1]

            div_pix_dx = (x-(d2w/2))%d2w
            div_pix_x = int((x-(d2w/2))/d2w)
            div_pix_dy = (y-(d2h/2))%d2h
            div_pix_y = int((y-(d2h/2))/d2h)
            i_c = (div_pix_y*out_width)+div_pix_x
            i_r = (div_pix_y*out_width)+div_pix_x+1
            i_d = ((div_pix_y+1)*out_width)+div_pix_x
            i_dr = ((div_pix_y+1)*out_width)+div_pix_x+1
            if((div_pix_x > 0) and (div_pix_dx < size[0])):
                output[i_c] += value
            if((div_pix_x < out_width-1) and (d2w-div_pix_dx < size[0])):
                output[i_r] += value
            if((div_pix_y < out_height-1) and (d2h-div_pix_dy < size[1])):
                output[i_d] += value
            if((div_pix_y < out_height-1) and (d2h-div_pix_dy < size[1])):
                if((div_pix_x < out_width-1) and (d2w-div_pix_dx < size[0])):
                    output[i_dr] += value
            
    return(output, out_width, out_height)
#------------------------------------------------------------------------------
def jpg_bytes_to_surf(buffer) -> pg.Surface:
    file = open("frame.jpeg", "wb")
    file.write(bytes(buffer))
    file.close()
    return(pg.image.load("frame.jpeg"))
#------------------------------------------------------------------------------
#...
capture_mode = CMD_ONLED
esp = Serial("COM17", 115200, timeout=1)
esp.read_until(bytes([S_END, S_END])) # If package incoming, wait for the end-start
esp.read_until(bytes([S_END])) # Skip that second package too
pg.init()
win = pg.display.set_mode((240*2, 240*2))
clock = pg.time.Clock()
#...
esp.write(bytes([CMD_ONLED]))
frame_surf = pg.Surface((240, 240))
frame_surf_clipped = pg.Surface(frame_surf.get_size())
running = True

font = pg.font.SysFont("arial", 8)
guess_pos = [0, 0]
beacon_led = False
field_old = []
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
        beacon_led = not beacon_led
        print(f"frame size: {len(frame)}b")
        if(len(frame) > 0):
            #...
            frame_surf_old = frame_surf
            frame_surf = jpg_bytes_to_surf(frame)
            #...
            size = (6, 6)
            div = (24, 24)
            field, fw, fh = collapse_target_color(frame_surf, (255, 255, 255), 50, div, size)
            d2x = frame_surf.get_width()/div[0]
            d2y = frame_surf.get_height()/div[1]
            #...
            if(len(field_old) == 0): field_old = field.copy()
            max_diff = 0
            max_diff_i = 0
            for i in range(len(field)):
                diff = (field[i] - field_old[i])
                if(abs(diff) > abs(max_diff)):
                    max_diff = diff
                    max_diff_i = i
            #...
            if((max_diff > 0 and beacon_led) or (max_diff < 0 and not beacon_led)):
                guess_pos = [((max_diff_i%fw)*d2x)+d2x/2, ((max_diff_i//fw)*d2y)+d2y/2]
            # Visualize
            max_val = 100
            for y in range(fh):
                for x in range(fw):
                    sx = (x*d2x)+d2x/2
                    sy = (y*d2y)+d2y/2
                    normal = round(field[(fw*y)+x]/max_val, 2)
                    pg.draw.circle(frame_surf, "orange", guess_pos, 5, 1)
                    #pg.draw.rect(frame_surf, "black", (sx- size[0], sy-size[1], size[0]*2, size[1]*2), 1)
                    fs = font.render(str(normal), 0, "red")
                    #frame_surf.blit(fs, (sx, sy))
            win.blit(pg.transform.scale_by(frame_surf, 2), (0, 0))
            field_old = field
    #...
    pg.display.update()
    #print("FPS:", round(clock.get_fps(), 1))
    clock.tick()
#------------------------------------------------------------------------------
