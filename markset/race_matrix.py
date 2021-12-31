
import asyncio

import neopixel
import board
import adafruit_framebuf


class RaceMatrix:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, update_ui_cb, framebuf=adafruit_framebuf.FrameBuffer(bytearray(60 * 10 * 3), 60, 10, buf_format=adafruit_framebuf.RGB888),fill_color=0xff0000, background_color=0x000000):
        print("race matrix init")
        self.framebuf_ = framebuf
        self.min_countdown_ = 3
        self.tens_seconds_countdown_ = 0
        self.seconds_countdown_ = 0
        self.update_ui_cb_ = update_ui_cb
        self.background_color_ = background_color
        self.fill_color_ = fill_color
        self.current_task_ = None
        self.loop_ = None

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


    def begin_timer(self, num_minutes):

        self.min_countdown_ = num_minutes
        self.tens_seconds_countdown_ = 0
        self.seconds_countdown_ = 0
        if self.current_task_ is None:
            loop = asyncio.get_running_loop()
            self.current_task_ = loop.create_task(self._timer())
            #loop.run_forever()

    async def _timer(self):
        while self.seconds_countdown_ >= 0 and self.tens_seconds_countdown_ >= 0 and self.min_countdown_ >= 0:
            self.count_down()
            await asyncio.sleep(1) # TODO: need to sleep to next full time second
        self.current_task_ = None

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
        if self.framebuf_.height < 10:
            raise Exception('numbers are currently 10 wide and 10 long')
        for i in range(self.framebuf_.height):
            bit_row = self.matrix_nums[num][i]
            # the numbers are currently 10 leds wide
            for j in range(9, -1, -1):
                # git bit is reversed
                # print(str(str(j) +  " " + str(bit_row) + " " + str(1 << j)))
                if self.get_bit(bit_row, j) == 1:
                    self.framebuf_.pixel(offset + (9 - j), i, self.fill_color_)
                else:
                    self.framebuf_.pixel(offset + (9 - j), i, self.background_color_)

    def get_bit(self, value, bit_index):
        # print(str(value) + " " + str(1 << bit_index) + " " + str(value & (1 << bit_index)))
        return value & (1 << bit_index) == (1 << bit_index)

    def get_matrix(self):
        index = 0
        matrix = []
        for y in range(self.framebuf_.height):  
            for x in range(self.framebuf_.width):  
                matrix.append(self.framebuf_.pixel(x, y))
        return matrix


        
        