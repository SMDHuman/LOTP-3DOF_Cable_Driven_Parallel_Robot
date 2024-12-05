from machine import Pin, PWM
from time import ticks_ms, sleep
from math import sqrt
from tomp import TOMP

cbrt = lambda x: x**(1.0/3.0)

class Stepper:
    max_dps: float = 200
    max_acc: float = 100
    max_jerk: float = 100
    #...
    def __init__(self, step: Pin, dir: Pin, en: Pin = None, m0: Pin = None, m1: Pin = None, m2: Pin = None, rv_step: int = 200) -> None:
        self.p_step = step
        self.p_dir = dir
        self.p_en = en
        self.p_modes = [m0, m1, m2]
        self.rv_step = rv_step
        if(type(self.p_modes[0]) == Pin):
            self.p_modes[0].off()
            self.p_modes[1].off()
            self.p_modes[2].off()
        self.mode: int = 0
        
        self.position: float = 0
        self.steps: int = 0
    #...
    def get_step2angle(self, step: int = 1) -> float:
        return(360*step/(self.rv_step*(2**self.mode)))
    #...
    def get_angle2step(self, angle: float = 1) -> int:
        return(round(self.rv_step*(2**self.mode)*angle/360))
    #...
    def set_mode(self, mode: int) -> None:
        self.mode = min(max(mode, 0), 7)
        self.p_modes[0].value((self.mode>>0) & 0x1)
        self.p_modes[1].value((self.mode>>1) & 0x1)
        self.p_modes[2].value((self.mode>>2) & 0x1)
    #...
    def config_movment(self, max_dps: float, max_accel: float, max_jerk: float) -> None:
        self.max_dps = max_dps
        self.max_acc = max_accel
        self.max_jerk = max_jerk
    #...
    @micropython.native
    def turn(self, angle: float, delay: float = 1) -> None:
        # Add carry
        real_pos = self.get_step2angle(self.steps)
        self.position += angle
        angle = self.position - real_pos
        #print("angle: ", angle)
        # Set Direction
        abs_angle = abs(angle)
        angle_sign = -1 if angle < 0 else 1
        if(angle < 0):
            self.p_dir.on()
        else:
            self.p_dir.off()
        #...
        turn_step = self.get_angle2step(abs_angle)
        if(turn_step < 1): return
        self.steps += turn_step * angle_sign
        dt: float = delay/turn_step
        #print(dt)
        for i in range(turn_step):
            self.p_step.toggle()
            self.p_step.toggle()
            sleep(dt)


