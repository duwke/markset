
import asyncio

import neopixel
import board
import adafruit_framebuf


class RaceMatrix:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, update_ui_cb, framebuf=adafruit_framebuf.FrameBuffer(bytearray(60 * 10 * 3), 60, 10, buf_format=adafruit_framebuf.RGB888),fill_color=0xff0000, background_color=0x000000):
        self.framebuf_ = framebuf
        self.min_countdown_ = 3
        self.tens_seconds_countdown_ = 0
        self.seconds_countdown_ = 0
        self.update_ui_cb_ = update_ui_cb
        self.background_color_ = background_color
        self.fill_color_ = fill_color
        self.current_task_ = None

        self.matrix_nums = [
            [
                0b0001111000,
                0b0011001100,
                0b0110000110,
                0b1100000011,
                0b1100000011,
                0b1100000011,
                0b1100000011,
                0b0110000110,
                0b0011001100,
                0b0001111000,
            ],[
                0b0001110000,
                0b0011110000,
                0b0110110000,
                0b0000110000,
                0b0000110000,
                0b0000110000,
                0b0000110000,
                0b0000110000,
                0b0000110000,
                0b1111111111,
            ],[
                0b0001111000,
                0b0110000110,
                0b1100000011,
                0b0000000011,
                0b0000001100,
                0b0000110000,
                0b0011000000,
                0b1100000000,
                0b1100000000,
                0b1111111111,
            ],[
                0b0011111100,
                0b1100000110,
                0b0000000011,
                0b0000000110,
                0b0000111000,
                0b0000000110,
                0b0000000011,
                0b0000000011,
                0b1100000110,
                0b0011111000,
            ],[
                0b0000000110,
                0b0000011110,
                0b0001100110,
                0b0110000110,
                0b1100000110,
                0b1111111111,
                0b0000000110,
                0b0000000110,
                0b0000000110,
                0b0000000110,
            ],[
                0b1111111111,
                0b1100000000,
                0b1100000000,
                0b1100000000,
                0b1111111100,
                0b0000000110,
                0b0000000011,
                0b0000000011,
                0b1100000110,
                0b0011111100,
            ],[
                0b0000111000,
                0b0011000000,
                0b0110000000,
                0b1100000000,
                0b1111111100,
                0b1100000110,
                0b1100000011,
                0b0110000110,
                0b0011001100,
                0b0001111000,
            ],[
                0b1111111110,
                0b0000000011,
                0b0000000011,
                0b0000000110,
                0b0000001100,
                0b0000011000,
                0b0000110000,
                0b0001100000,
                0b0011000000,
                0b0110000000,
            ],[
                0b0001111000,
                0b0110000110,
                0b1100000011,
                0b0110000110,
                0b0001111000,
                0b0110000110,
                0b1100000011,
                0b1100000011,
                0b0110000110,
                0b0011111100,
            ],[
                0b0001111000,
                0b0110000110,
                0b1100000011,
                0b0110000011,
                0b0001111111,
                0b0000000011,
                0b0000000011,
                0b0000000011,
                0b0000000110,
                0b0001111000,
            ]
        ]

        self.framebuf_.fill(background_color)
        self.update_ui_cb_(self.get_matrix())

        # pixel_pin = board.D21
        # num_pixels = 600
        # ORDER = neopixel.RGB
        # pixels = neopixel.NeoPixel(
        #     pixel_pin, num_pixels, brightness=0.2, auto_write=True, pixel_order=ORDER
        # )
        # pixel_framebuf = PixelFramebuffer(
        #     pixels,
        #     60,
        #     10,
        #     orientation=PixelFramebuffer.VERTICAL,
        #     rotation=2)

    def begin_timer(self, num_minutes):

        self.min_countdown_ = num_minutes
        self.tens_seconds_countdown_ = 0
        self.seconds_countdown_ = 0
        if self.current_task_ is None:
            self.current_task_ = asyncio.get_event_loop().create_task(self._timer())

    async def _timer(self):
        while self.seconds_countdown_ >= 0 and self.tens_seconds_countdown_ >= 0 and self.min_countdown_ >= 0:
            self.CountDown()
            await asyncio.sleep(1) # TODO: need to sleep to next full time second

    def count_down(self):
        self.seconds_countdown_ -= 1
        if(self.seconds_countdown_ < 0):
            self.seconds_countdown_ = 9
            self.tens_seconds_countdown_ -= 1
        if(self.tens_seconds_countdown_ < 0):
            self.tens_seconds_countdown_ = 5
            self.min_countdown_ -= 1

        self.display_big_number(0, self.min_countdown_, True)
        self.display_big_number(13, self.tens_seconds_countdown_, False)
        self.display_big_number(24, self.seconds_countdown_, False)

        self.update_ui_cb_(self.get_matrix())


    def display_big_number(self, offset, num, debug):
        if self.rows_ < 10:
            raise Exception('numbers are currently 10 wide and 10 long')
        for i in range(self.rows_):
            bit_row = self.matrix_nums[num][i]
            start_index = (self.columns_ * i) + offset
            # the numbers are currently 10 leds wide
            for j in range(9, -1, -1):
                # git bit is reversed
                print(str(start_index) + " " + str(j) +  " " + str(bit_row) + " " + str(1 << j))
                if self.get_bit(bit_row, j) == 1:
                    self.framebuf_.pixel(i, offset + (9 - j), self.fill_color_)
                else:
                    self.framebuf_.pixel(i, offset + (9 - j), self.background_color_)

    def get_bit(self, value, bit_index):
        # print(str(value) + " " + str(1 << bit_index) + " " + str(value & (1 << bit_index)))
        return value & (1 << bit_index) == (1 << bit_index)

    def get_matrix(self):
        index = 0
        matrix = []
        for x in range(self.framebuf_.width):  
            for y in range(self.framebuf_.height):  
                matrix.append(self.framebuf_.pixel(x, y))
        return matrix


        
        