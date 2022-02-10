
import asyncio

import race_matrix
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
class RaceManager:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, race_matrix, horn):
        print("race matrix init")   
        self.leds_ = race_matrix
        self.horn_ = horn
        self.seconds_countdown_ = 0
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

    def begin_racing(self):
        # set mode
        self.mode_ = MODE.RACING
        with open("markset/config.yaml", "r") as stream:
            try:
                self.config_ = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        num_seconds = 180 * len(self.config_['order'])
        self.begin_timer_(1)

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
                self.count_down_tick()
            if self.mode_ == MODE.SHOW_ORDER:
                self.show_order_tick()
            if self.mode_ == MODE.RACING:
                await self.racing_tick()

            self.tick_index_ += 1

            self.leds_.copy_matrix_to_led()

            duration = time.time() - self.start_time_
            num_ticks = int(duration / self.seconds_per_tick_)
            if num_ticks <= self.tick_index_:
                # just sleep enough to get to the next tick.
                mill_seconds_til_next_tick = ((self.tick_index_ + 1) * self.seconds_per_tick_) - duration
                logging.warn("ticks " + str(num_ticks) + "/" + str(self.ticks_total_))
                await asyncio.sleep(mill_seconds_til_next_tick) 
        logging.warn("stop task")
        self.leds_.fill_color(self.background_color_)
        self.current_task_ = None
        if self.mode_ == MODE.COUNTDOWN:
            self.begin_show_order()


    def show_order_tick(self):
        # for each order, give 4 seconds pause, then scroll for 6?
        # determine bottom index (not the scroller), then top index, which will scroll
        # 
        bottom_index = 0
        num_seconds_in = self.tick_index_ * self.seconds_per_tick_
        if num_seconds_in > self.pause_seconds:
            bottom_index = int((num_seconds_in - self.pause_seconds) / (self.pause_seconds + self.scroll_seconds)) + 1

        if bottom_index + 1 > len(self.config_['order']):
            return

        self.leds_.fill_color(self.config_['order'][bottom_index]['color'])
        self.leds_.fill_text(str(bottom_index + 1) + "-" + self.config_['order'][bottom_index]['name'], 1, 2, 0xffffff)

        if num_seconds_in > self.pause_seconds:
            top_index = int(num_seconds_in / (self.pause_seconds + self.scroll_seconds)) 

            # is the bottom the only thing shown?
            ticks_in_this_index = self.tick_index_ - ((top_index) * (self.pause_seconds + self.scroll_seconds) / self.seconds_per_tick_)
            is_paused = ticks_in_this_index < self.pause_seconds / self.seconds_per_tick_
            logging.warn("is_paused " + str(is_paused) + " " + str(ticks_in_this_index))
            if not is_paused:                
                # overwrite new row with old row for shifting affect. determine how much we shift by.
                ticks_into_scrolling = self.tick_index_ - ((top_index) * (self.pause_seconds + self.scroll_seconds) / self.seconds_per_tick_) - (self.pause_seconds / self.seconds_per_tick_)
                offset_x = int((ticks_into_scrolling / (self.scroll_seconds / self.seconds_per_tick_)) * self.framebuf_.width)

                logging.warn("frame_x " + str(self.tick_index_) + " " + str(offset_x) + " " + str(ticks_into_scrolling))
                self.leds_.write_over_frame(str(top_index + 1) + "-" + self.config_['order'][top_index]['name'], 0xffffff, self.config_['order'][top_index]['color'], offset_x, 2)


    async def racing_tick(self):
        await self.horn_.play_tone(5)
        self.mode_ = MODE.WAITING
        self.current_task_ = None

    def count_down_tick(self):
        # tick every second
        if (self.tick_index_ * self.seconds_per_tick_) % 1.0 == 0:
            self.seconds_countdown_ -= 1
            num_min = int(self.seconds_countdown_ / 60)
            seconds_remaining = self.seconds_countdown_ % 60

            # self.display_big_number(0, self.min_countdown_, True)
            # self.display_big_number(13, self.tens_seconds_countdown_, False)
            # self.display_big_number(24, self.seconds_countdown_, False)
            self.leds_.fill_color(self.background_color_)
            self.framebuf_.text(str(num_min) + ":" + str(seconds_remaining).zfill(2), 1, 1, self.fill_color_)




        
        