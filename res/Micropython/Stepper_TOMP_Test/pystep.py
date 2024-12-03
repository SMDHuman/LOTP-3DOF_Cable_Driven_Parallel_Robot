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
        self.mode = 0
    #...
    def get_step_angle(self) -> float:
        return(360 / (self.rv_step*(2**self.mode)))
    #...
    def set_mode(self, mode: int) -> None:
        self.mode = mode
        self.p_modes[0].value((mode>>0) & 0x1)
        self.p_modes[1].value((mode>>1) & 0x1)
        self.p_modes[2].value((mode>>2) & 0x1)
    #...
    def config_movment(self, max_dps: float, max_accel: float, max_jerk: float) -> None:
        self.max_dps = max_dps
        self.max_acc = max_accel
        self.max_jerk = max_jerk
    #...
    def turn(self, angle: float, delay: float = 10**-3) -> None:
        if(angle < 0):
            self.p_dir.on()
            angle = -angle
        else:
            self.p_dir.off()
        total_steps = round(self.rv_step*(2**self.mode)*angle*2/360)
        for i in range(total_steps):
            self.p_step.toggle()
            sleep(delay/total_steps)
    #...
    @micropython.native
    def tomp_turn(self, angle: float) -> None:
        if(angle < 0):
            self.p_dir.on()
            angle = -angle
        else:
            self.p_dir.off()
        #...
        tomp = TOMP()
        tomp.config(angle, self.max_dps, self.max_acc, self.max_jerk)
        #...
        st: float = ticks_ms()/1000
        t: float = st
        angle_current: float = 0
        while(not tomp.end):
            old_t: float = t
            t = ticks_ms()/1000 - st
            dt: float = t - old_t
            angle_target: float = tomp.get_pos(t)
            #...
            sa: float = self.get_step_angle()
            step: float = (angle_target - angle_current)/sa
            istep: int = int(step)
            if(step >= 1):
                #print(step, dt)
                for i in range(istep):
                    self.p_step.toggle()
                    self.p_step.toggle()
                    sleep(dt/istep)
                angle_current += sa*istep

