
import board
import random
import asyncio
from neopixel import NeoPixel

class LedTest():

    def __init__(self):
        self.data = []
        self.num_leds = 10
        self.pinColors = []
        self.np = NeoPixel(board.D18, self.num_leds)   # create NeoPixel driver on GPIO0

    def turn_off(self):
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def raindow(self):
        for i in range(self.num_leds - 1, 1, -1):
            self.np[i - 1] = self.np[i]
        self.np[0] = (random.randint(0, 254), random.randint(0, 254), random.randint(0, 254))

    def delete(self, data):
        self.turn_off()
        return {'message': 'changed', 'value': 'off'}

    def start_rainbow(self, data):
        """Return list of all customers"""
        loop = asyncio.get_running_loop()
        self.current_task_ = loop.create_task(self.raindow())
