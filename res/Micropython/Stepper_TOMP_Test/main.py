from machine import Pin, PWM
import time
from pystep import Stepper
from tomp import TOMP


led = Pin("LED", Pin.OUT)

mode = 1
mode_pins = [Pin(i, Pin.OUT, value = 0) for i in range(13, 10, -1)]
step_pin = Pin(9, Pin.OUT, value = 0)
dir_pin = Pin(8, Pin.OUT, value = 0)
switch_pin = Pin(15, Pin.IN)

motor = Stepper(step_pin, dir_pin, m0=mode_pins[0], m1=mode_pins[1], m2=mode_pins[2])
motor.set_mode(3)

reset_last_ms: int = time.time_ns() // 10**6
def pos_reset(pin):
    global reset_last_ms
    now_ms: int = time.time_ns() // 10**6
    if(now_ms - reset_last_ms < 500): return
    reset_last_ms = now_ms
    
    print("Hey!!!")

def tomp_turn(target: float, Vmax: float = 200, Amax: float = 50, Jmax: float = 100):
    tomp = TOMP(target, Vmax, Amax, Jmax)
    #...
    tomp_div = 100
    dt = tomp.get_path_time()/tomp_div
    old_pos = 0
    motor_start_pos = motor.position
    for i in range(1, tomp_div):
        it = i/tomp_div
        #...
        t = tomp.get_path_time() * it
        #...
        pos = tomp.get_pos(t)
        #print("pos: ", pos)
        motor.turn(pos - old_pos, dt)
        old_pos = pos
    motor.turn(target - (motor.position-motor_start_pos), dt)

switch_pin.irq(pos_reset, Pin.IRQ_FALLING)

dt = 0.5
while(True):
    led.on()
    tomp_turn(360*3)
    print(motor.position)
    print(motor.steps)
    led.off()
    tomp_turn(-180*3)
    print(motor.position)
    print(motor.steps)