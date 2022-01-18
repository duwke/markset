
import asyncio

import neopixel
import board
import adafruit_framebuf
import yaml
from enum import Enum
import time
import logging


class MODE(Enum):
    WAITING = 0
    COUNTDOWN = 1
    SHOW_ORDER = 2
    RACING = 3
class RaceMatrix:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, pixels, width, height, fill_color=0xff0000, background_color=0x000000):
        print("race matrix init")   
        self.pixels_ = pixels
        self.framebuf_ = adafruit_framebuf.FrameBuffer(bytearray(width * height * 3), width, height, buf_format=adafruit_framebuf.RGB888)
        self.top_framebuf_ = adafruit_framebuf.FrameBuffer(bytearray(self.framebuf_.width * self.framebuf_.height * 4), self.framebuf_.width, self.framebuf_.height, buf_format=adafruit_framebuf.RGB888)
        self.seconds_countdown_ = 0
        self.background_color_ = background_color
        self.fill_color_ = fill_color
        self.current_task_ = None
        self.order_index_ = 0
        self.mode_ = MODE.WAITING
        self.start_time_ = None
        self.seconds_per_tick_ = .2 # 5 hz ticks
        self.tick_index_ = 0 # the number of _timer ticks.  Keep this so we always tick the correct number of times, even if we get behind.
        self.ticks_total_ = 0 # for each mode, we set the number of expected ticks at the desired frequency
        self.seconds_countdown_ = 0
        self.config_ = None
        self.pause_seconds = 1
        self.scroll_seconds = 3

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
        num_seconds = (self.pause_seconds * self.scroll_seconds) * len(self.config_['order'])
        self.begin_timer_(num_seconds)
        
    def begin_countdown(self, seconds):
        # set mode
        self.mode_ = MODE.COUNTDOWN
        self.begin_timer_(seconds)

        
    def begin_timer_(self, seconds):
        # kick the timer
        self.start_time_ = time.time()
        self.ticks_total_ = int(seconds / self.seconds_per_tick_)
        self.seconds_countdown_ = seconds                                               
        self.tick_index_ = 0
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

            if self.pixels_ is not None:
                self.copy_matrix_to_led()

            duration = time.time() - self.start_time_
            num_ticks = int(duration / self.seconds_per_tick_)
            if num_ticks <= self.tick_index_:
                # just sleep enough to get to the next tick.
                mill_seconds_til_next_tick = ((self.tick_index_ + 1) * self.seconds_per_tick_) - duration
                logging.warn("ticks " + str(num_ticks) + "/" + str(self.ticks_total_))
                await asyncio.sleep(mill_seconds_til_next_tick) 
        logging.warn("stop task")
        self.framebuf_.fill(self.background_color_)
        if self.pixels_ is not None:
            self.copy_matrix_to_led()
        self.current_task_ = None
    
    def copy_matrix_to_led(self):
        # start at top left
        for y in range(self.framebuf_.height):
            led_matrix_y = y
            for x in range(self.framebuf_.width):
                if y % 2 != 0:
                    self.pixels_[led_matrix_y * self.framebuf_.width + x] = self.framebuf_.pixel(x, y)
                else:
                    self.pixels_[led_matrix_y * self.framebuf_.width + self.framebuf_.width - x - 1] = self.framebuf_.pixel(x, y)

        self.pixels_.show()

    def show_order(self):
        # for each order, give 4 seconds pause, then scroll for 6?
        # determine bottom index (not the scroller), then top index, which will scroll
        # 
        bottom_index = 0
        num_seconds_in = self.tick_index_ * self.seconds_per_tick_
        if num_seconds_in > self.pause_seconds:
            bottom_index = int((num_seconds_in - self.pause_seconds) / (self.pause_seconds + self.scroll_seconds)) + 1

        if bottom_index + 1 > len(self.config_['order']):
            return

        self.framebuf_.fill(self.config_['order'][bottom_index]['color'])
        self.framebuf_.text(str(bottom_index + 1) + "-" + self.config_['order'][bottom_index]['name'], 1, 2, 0xffffff)

        if num_seconds_in > self.pause_seconds:
            top_index = int(num_seconds_in / (self.pause_seconds + self.scroll_seconds)) 

            # is the bottom the only thing shown?
            ticks_in_this_index = self.tick_index_ - ((top_index) * (self.pause_seconds + self.scroll_seconds) / self.seconds_per_tick_)
            is_paused = ticks_in_this_index < self.pause_seconds / self.seconds_per_tick_
            logging.warn("is_paused " + str(is_paused) + " " + str(ticks_in_this_index))
            if not is_paused:
                self.top_framebuf_.fill(self.config_['order'][top_index]['color'])
                self.top_framebuf_.text(str(top_index + 1) + "-" + self.config_['order'][top_index]['name'], 1, 2, 0xffffff)
                
                # determine how much we shift by.
                ticks_into_scrolling = self.tick_index_ - ((top_index) * (self.pause_seconds + self.scroll_seconds) / self.seconds_per_tick_) - (self.pause_seconds / self.seconds_per_tick_)
                frame_x = int((ticks_into_scrolling / (self.scroll_seconds / self.seconds_per_tick_)) * self.framebuf_.width)

                logging.warn("frame_x " + str(self.tick_index_) + " " + str(frame_x) + " " + str(ticks_into_scrolling))
                # copy top frame 
                for y in range(self.framebuf_.height):  
                    for x in range(self.framebuf_.width) :  
                        self.framebuf_.pixel(x + frame_x, y, self.top_framebuf_.pixel(x, y))


    def show_racing(self):
        pass

    def count_down(self):
        # tick every second
        if (self.tick_index_ * self.seconds_per_tick_) % 1.0 == 0:
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


        
        