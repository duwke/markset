


from machine import Pin
from neopixel import NeoPixel
from markset.race_matrix import Matrix

class matrix:

    def __init__(self, rows, columns, io_pin):
        self.matrix = Matrix.Matrix(rows, columns, self.DisplayMatrix)

        pin = Pin(io_pin, Pin.OUT)   # set GPIO0 to output to drive NeoPixels
        self.np = NeoPixel(pin, self.rows_ * self.columns_)   # create NeoPixel driver on GPIO0

    def BeginTimer(self, num_minutes):
        self.timer_ = Timer(3)
        self.timer_.init(mode=Timer.Timer.PERIODIC, period=1000, callback=self.CountDown)  
        self.min_countdown = num_minutes
        self.tens_seconds_countdown = 0
        self.seconds_countdown = 0

    def CountDown(self):
        self.seconds_countdown -= 1
        if(self.seconds_countdown < 0):
            self.seconds_countdown = 9
            self.tens_seconds_countdown -= 1
        if(self.tens_seconds_countdown < 0):
            self.tens_seconds_countdown = 5
            self.min_countdown -= 1

    def DisplayMatrix(self, data):

        
        