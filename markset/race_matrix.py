
import asyncio

import neopixel
import board
import adafruit_framebuf
import yaml
from enum import Enum
import time


class MODE(Enum):
    WAITING = 0
    COUNTDOWN = 1
    SHOW_ORDER = 2
    RACING = 3
class RaceMatrix:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, framebuf=adafruit_framebuf.FrameBuffer(bytearray(60 * 10 * 3), 60, 10, buf_format=adafruit_framebuf.RGB888),fill_color=0xff0000, background_color=0x000000):
        print("race matrix init")
        self.framebuf_ = framebuf
        self.seconds_countdown_ = 0
        self.background_color_ = background_color
        self.fill_color_ = fill_color
        self.current_task_ = None
        self.order_index_ = 0
        self.mode_ = MODE.WAITING
        self.start_time_ = None
        self.tick_seconds_ = .25 # 4 hz ticks
        self.tick_index_ = 0 # the number of _timer ticks.  Keep this so we always tick the correct number of times, even if we get behind.
        self.ticks_total_ = 0 # for each mode, we set the number of expected ticks at the desired frequency
        self.seconds_countdown_ = 0
        self.config_ = None

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

    def begin_racing(self):
        # set mode
        self.mode_ = MODE.RACING
        with open("markset/config.yaml", "r") as stream:
            try:
                self.config_ = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        num_seconds = 180 * len(self.config_['order'])
        self.begin_timer_(num_seconds)

    def begin_show_order(self):
        # set mode
        self.mode_ = MODE.SHOW_ORDER
        with open("markset/config.yaml", "r") as stream:
            try:
                self.config_ = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        num_seconds = 10 * len(self.config_['order'])
        self.begin_timer_(num_seconds)
        
    def begin_countdown(self, seconds):
        # set mode
        self.mode_ = MODE.COUNTDOWN
        self.begin_timer_(seconds)

        
    def begin_timer_(self, seconds):
        # kick the timer
        self.start_time_ = time.time()
        self.ticks_total_ = int(seconds / self.tick_seconds_)
        self.seconds_countdown_ = seconds
        if self.current_task_ is None:
            loop = asyncio.get_running_loop()
            self.current_task_ = loop.create_task(self._timer())

    async def _timer(self):
        ### update based on remaining ticks.  If we are behind, don't sleep.
        while self.tick_index_ <  self.ticks_total_:
            if self.mode_ == MODE.COUNTDOWN:
                self.count_down()
            if self.mode_ == MODE.SHOW_ORDER:
                self.show_order()
            if self.mode_ == MODE.RACING:
                self.show_racing()

            self.tick_index_ += 1

            duration = time.time() - self.start_time_
            num_ticks = int(duration / self.tick_seconds_)
            if num_ticks <= self.tick_index_:
                # just sleep enough to get to the next tick.
                mill_seconds_til_next_tick = ((self.tick_index_ + 1) * self.tick_seconds_) - duration
                await asyncio.sleep(mill_seconds_til_next_tick) 
        self.current_task_ = None

    def show_order(self):
        # for each order, give 4 seconds pause, then scroll for 6?
        # determine bottom index (not the scroller), then top index, which will scroll
        # 
        pause_seconds = 4
        scroll_seconds = 6
        bottom_index = 0
        num_seconds_in = self.tick_index_ * self.tick_seconds_
        if num_seconds_in > pause_seconds:
            bottom_index = int((num_seconds_in - pause_seconds) / (pause_seconds + scroll_seconds)) + 1
        
        self.framebuf_.fill(self.config_['order'][bottom_index]['color'])
        self.framebuf_.text(str(bottom_index + 1) + ":" + self.config_['order'][bottom_index]['name'], 0, 2, 0xffffff)

        top_index = int(num_seconds_in / (pause_seconds + scroll_seconds)) 
        seconds_shown_on_board = (int(num_seconds_in) % (pause_seconds + scroll_seconds)) 
        if seconds_shown_on_board > pause_seconds:
            ticks_per_index = (num_seconds_in + pause_seconds) / self.tick_seconds_
            # this index has ben shown for this many ticks
            ticks_showing_index = self.tick_index_ - (ticks_per_index * top_index)
            num_ticks_scrolling = ticks_showing_index - (pause_seconds / self.tick_seconds_)
            # num_ticks_scrolling corrosponds to the x
            total_ticks_scrolling = scroll_seconds / self.tick_seconds_
            frame_x =  int(self.framebuf_.width * (num_ticks_scrolling / total_ticks_scrolling))
            # todo: scroll background too.  Blit would have been nice
            self.framebuf_.text(str(top_index + 1) + "-" + self.config_['order'][top_index]['name'], frame_x, 2, 0xffffff)


    def show_racing(self):
        pass

    def count_down(self):
        # tick every second
        if (self.tick_index_ * self.tick_seconds_) % 1.0 == 0:
            self.seconds_countdown_ -= 1
            num_min = int(self.seconds_countdown_ / 60)
            seconds_remaining = self.seconds_countdown_ % 60

            # self.display_big_number(0, self.min_countdown_, True)
            # self.display_big_number(13, self.tens_seconds_countdown_, False)
            # self.display_big_number(24, self.seconds_countdown_, False)

            self.framebuf_.fill(self.background_color_)
            self.framebuf_.text(str(num_min) + ":" + str(seconds_remaining).zfill(2), 1, 1, self.fill_color_)




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
        matrix_info = {}
        matrix_info['rows'] = self.framebuf_.height
        matrix_info['columns'] = self.framebuf_.width
        matrix = []
        for y in range(self.framebuf_.height):  
            for x in range(self.framebuf_.width):  
                matrix.append(self.framebuf_.pixel(x, y))
        matrix_info['matrix_data'] = matrix
        return matrix_info


        
        