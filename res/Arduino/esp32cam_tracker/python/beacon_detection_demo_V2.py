from serial import Serial
from PIL import Image
import pygame as pg
import numpy as np
import time
import math


# Constants
S_END = 0xC0
S_ESC = 0xDB
S_ESC_END = 0xDC
S_ESC_ESC = 0xDD
CMD_TRIGGER = 0x0A
CMD_ONESHOT = 0x0B
CMD_STREAM = 0x0C
CMD_ONLED = 0x0D

class App:
    running = True
    calibrating = False
    calib_frame_count = 0
    led_status = False
    def __init__(self): 
        global font    
        pg.init()
        pg.font.init()
        font = pg.font.SysFont("arial", 10)
        self.win = pg.display.set_mode((480, 480))
        #...
        self.esp = Serial("COM17", 115200, timeout=1)
        self.esp.read_until(bytes([S_END, S_END])) # If package incoming, wait for the end-start
        self.esp.read_until(bytes([S_END])) # Skip that second package too
        self.esp.write(bytes([CMD_ONLED]))
        #...
        self.clock = pg.time.Clock()
        #...
        self.run()
    #--------------------------------------------------------------------------
    def event_task(self):
        for event in pg.event.get():
            if(event.type == pg.QUIT):
                pg.quit()
                self.running = False
            if(event.type == pg.KEYDOWN):
                if(event.key == pg.K_SPACE):
                    self.calibrating = True
                    self.calib_frame_count = 0
    #--------------------------------------------------------------------------
    def get_frame(self) -> list[int]:
        while((int(self.esp.read(1)[0]) != S_END)):
            pass
        data_buf = self.esp.read_until(bytes([S_END]))
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
    #--------------------------------------------------------------------------
    def jpg_bytes_to_surf(self, buffer) -> pg.Surface:
        file = open("frame.jpg", "wb")
        file.write(bytes(buffer))
        file.close()
        return(pg.image.load("frame.jpg"))
    #--------------------------------------------------------------------------
    def process_highlights(self, surf: pg.Surface, size: tuple[int, int])-> list[list[float]]:
        output: list[list[float]] = [[0.0]*size[0] for i in range(size[1])]
        sw, sh = surf.get_size()
        #...
        for y in range(sh):
            for x in range(sw):
                color = surf.get_at((x, y))[0]
                ox = int(x*size[0]/sw)
                oy = int(y*size[1]/sh)
                output[oy][ox] += color
        #...
        return(output)
    #--------------------------------------------------------------------------
    def visualize_frame(self, surf, frame, div = 1):
        cw, ch = surf.get_size()
        fw, fh = len(frame), len(frame[0])
        for y in range(len(frame)):
            for x in range(len(frame[y])):
                value = round(frame[y][x]/div, 1)
                txt_surf = font.render(str(value), 0, "red")
                pg.draw.rect(surf, "black", (x*cw/fw, y*ch/fh, cw/fw, ch/fh), 1)
                surf.blit(txt_surf, (x*cw/fw, y*ch/fh))
    #--------------------------------------------------------------------------
    def find_frame_min(self, frame):
        min_val = 0
        min_pos = [0, 0]
        for y in range(len(frame)):
            for x in range(len(frame[y])):
                if(frame[y][x] < min_val):
                    min_val = frame[y][x]
                    min_pos = [x, y]
        return(min_val, min_pos)
    #--------------------------------------------------------------------------
    def find_frame_max(self, frame):
        max_val = 0
        max_pos = [0, 0]
        for y in range(len(frame)):
            for x in range(len(frame[y])):
                if(frame[y][x] > max_val):
                    max_val = frame[y][x]
                    max_pos = [x, y]
        return(max_val, max_pos)
    #--------------------------------------------------------------------------
    def run(self):
        old_frame = None
        diff_frame = None
        old_diff_frame = None
        diff_calib_frame = None
        cam_img = pg.Surface((240, 240))
        self.win.fill("gray")
        while(True):
            self.event_task()
            if(not self.running): return
            # Draw camera
            if(self.esp.in_waiting):
                self.led_status = not self.led_status
                cam_img = self.jpg_bytes_to_surf(self.get_frame())
                self.win.blit(cam_img, (0, 0))
                # Visualize brightness frame
                frame = self.process_highlights(cam_img, (24, 24))
                surf = cam_img.copy()
                self.visualize_frame(surf, frame, div = 100)
                self.win.blit(surf, (240, 0))
                # Visualize difference frame
                surf = cam_img.copy()
                if(old_frame):
                    if(diff_frame):
                        old_diff_frame = [row.copy() for row in diff_frame]
                    diff_frame = [row.copy() for row in frame]
                    for y in range(len(frame)):
                        for x in range(len(frame[y])):
                            diff_frame[y][x] -= old_frame[y][x]
                            # If calibrated, apply threshold
                            if(diff_calib_frame):
                                if(abs(diff_frame[y][x]) <= diff_calib_frame[y][x]):
                                    diff_frame[y][x] = 0
                    self.visualize_frame(surf, diff_frame, 100)
                    self.win.blit(surf, (0, 240))
                # Calibrate the threshold
                if(self.calibrating and diff_frame):
                    pg.draw.circle(self.win, "red", (10, 10), 10)
                    if(self.calib_frame_count > 20):
                        self.calibrating = False
                    else:
                        self.calib_frame_count += 1
                        if(not diff_calib_frame): 
                            diff_calib_frame = [row.copy() for row in diff_frame]
                        #...
                        for y in range(len(diff_calib_frame)):
                            for x in range(len(diff_calib_frame[y])):
                                if(abs(diff_frame[y][x]) > diff_calib_frame[y][x]):
                                    diff_calib_frame[y][x] = abs(diff_frame[y][x])
                # Find blink
                if(diff_frame and old_diff_frame):
                    surf = cam_img.copy()
                    if(self.led_status):
                        v, guess1 = self.find_frame_max(diff_frame)
                        v, guess2 = self.find_frame_min(old_diff_frame)
                    else:
                        v, guess1 = self.find_frame_min(diff_frame)
                        v, guess2 = self.find_frame_max(old_diff_frame)
                    cw, ch = surf.get_size()
                    fw, fh = len(diff_frame), len(diff_frame[0])
                    pg.draw.circle(surf, "orange", ((guess1[0]+.5)*cw/fw, (guess1[1]+.5)*ch/fh), 10, 3)
                    pg.draw.circle(surf, "orange", ((guess1[0]+.5)*cw/fw, (guess1[1]+.5)*ch/fh), 10, 3)
                    for y in range(len(diff_frame)):
                        for x in range(len(diff_frame[y])):
                            txt_surf = font.render(str([x, y]), 0, "red")
                            pg.draw.rect(surf, "black", (x*cw/fw, y*ch/fh, cw/fw, ch/fh), 1)
                            #surf.blit(txt_surf, (x*cw/fw, y*ch/fh))
                    self.win.blit(surf, (240, 240))

                #...
                old_frame = [row.copy() for row in frame]
            #...
            pg.display.update()
            self.clock.tick(30)
App()