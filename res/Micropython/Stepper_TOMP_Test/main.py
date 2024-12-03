from machine import Pin, PWM
import time
from pystep import Stepper

led = Pin(25, Pin.OUT)

mode = 1
mode_pins = [Pin(i, Pin.OUT, value = 0) for i in range(11, 14)]
step_pin = Pin(14, Pin.OUT, value = 0)
dir_pin = Pin(15, Pin.OUT, value = 0)

motor = Stepper(step_pin, dir_pin, m0=mode_pins[0], m1=mode_pins[1], m2=mode_pins[2])
motor.set_mode(3)
motor.max_dps = 180
motor.max_acc = 180
motor.max_jerk = 180

dt = 0.5
while(True):
    led.on()
    motor.tomp_turn(-90)
    led.off()
    motor.tomp_turn(360)