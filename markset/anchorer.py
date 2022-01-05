
import asyncio

import neopixel
import board
import adafruit_framebuf
import yaml
from enum import Enum
import time
from time import sleep
import digitalio
import pwmio
import logging
import pigpio

class Anchorer:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, framebuf=adafruit_framebuf.FrameBuffer(bytearray(60 * 10 * 3), 60, 10, buf_format=adafruit_framebuf.RGB888),fill_color=0xff0000, background_color=0x000000):
        print("achorer init")

        self.dir_ = digitalio.DigitalInOut(board.D16)
        self.dir_.switch_to_output()
        self.pulse_ = digitalio.DigitalInOut(board.D6)
        self.pulse_.switch_to_output()
        self.enable_ = digitalio.DigitalInOut(board.D26)
        self.enable_.switch_to_output()
        self.CW = 1
        self.CCW = 0
        self.spr_ = 400 # steps per revolution

        self.enable_.value = 1 # this turns it off?

        self.delay = 2 / self.spr_ # three second revolution
        self.stop_ = False

        #self.pwm_ = pwmio.PWMOut(board.D19, frequency=200, duty_cycle=0, variable_frequency=False)
        self.pi_ = pigpio.pi()
        

    async def move(self):
        self.enable_.value = 0
        self.stop_ = False
        sleep(.5)
        logging.warn("set duty cycle")
        self.pi_.set_PWM_dutycycle(19, 255*0.50)
        self.pi_.set_PWM_frequency(19, 3200)
        while not self.stop_:
            logging.warn("check sleep")
            await asyncio.sleep(.5) #release the thread every so often
        self.pi_.set_PWM_dutycycle(19, 0)
        self.enable_.value = 1
        
    
    def begin_forward(self):

        self.enable_.value = 1
        sleep(.5)
        self.dir_.value = self.CCW
        loop = asyncio.get_running_loop()
        self.current_task_ = loop.create_task(self.move())

    def begin_reverse(self):

        self.enable_.value = 1
        sleep(.5)
        self.dir_.value = self.CW
        loop = asyncio.get_running_loop()
        self.current_task_ = loop.create_task(self.move())

    def stop(self):
        self.stop_ = True

    def clear_stop(self):
        self.stop_ = False
        