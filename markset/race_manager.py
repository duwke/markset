
import asyncio
from distutils.command.config import config

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
        self.ticks_per_second_ = 5 
        self.tick_index_ = 0 # the number of _timer ticks.  Keep this so we always tick the correct number of times, even if we get behind.
        self.show_order_tick_index = 0 # same as above for SHOW_ORDER, but can be reset for RACING to show order during
        self.ticks_total_ = 0 # for each mode, we set the number of expected ticks at the desired frequency
        self.config_ = None
        self.pause_seconds = 1
        self.scroll_seconds = 3
        self.countdown_time_ = 0 # during the prestart or racing, we use this to determine where in the array we are.
        self.music_countdown = 0 # start music.  set to x, and once it gets to 0, we call stop.
        self.class_index_ = -1 # -1 is prestart
        self.timeline_function_ = ""
        with open("markset/config.yaml", "r") as stream:
            try:
                self.config_ = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def begin_racing(self):
        # set mode
        self.mode_ = MODE.RACING
        self.class_index_ = -1
        self.countdown_time_ = 0
        prestart_length = self.config_["prestart_timeline"][0]
        class_timeline_length = self.config_["class_timeline"][0]
        num_seconds = prestart_length + class_timeline_length * len(self.config_['order'])
        self.seconds_countdown_ = prestart_length
        self.begin_timer_(num_seconds)

    def begin_show_order(self):
        # set mode
        self.mode_ = MODE.SHOW_ORDER
        num_seconds = (self.pause_seconds * self.scroll_seconds) * len(self.config_['order'])
        self.show_order_tick_index = 0
        self.begin_timer_(num_seconds)
        
    def begin_countdown(self, seconds):
        # set mode
        self.mode_ = MODE.COUNTDOWN
        self.begin_timer_(seconds)

        
    def begin_timer_(self, seconds):
        # kick the timer
        self.start_time_ = time.time()
        self.ticks_total_ = int(seconds * self.ticks_per_second_)
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
                if self.class_index_ == -1:
                    await self.racing
                await self.racing_tick()

            self.tick_index_ += 1
            self.show_order_tick_index += 1

            self.leds_.copy_matrix_to_led()

            duration = time.time() - self.start_time_
            num_ticks = int(duration * self.ticks_per_second_)
            if num_ticks <= self.tick_index_:
                # just sleep enough to get to the next tick.
                mill_seconds_til_next_tick = ((self.tick_index_ + 1) / self.ticks_per_second_) - duration
                logging.warn("ticks " + str(num_ticks) + "/" + str(self.ticks_total_))
                await asyncio.sleep(mill_seconds_til_next_tick) 
        logging.warn("stop task")
        self.leds_.fill_color(self.background_color_)
        self.current_task_ = None
        if self.mode_ == MODE.COUNTDOWN:
            self.begin_show_order()


    async def racing_tick(self):

        timeline = self.config_['prestart_timeline']
        music = None
        sail_class = None
        if self.class_index_ < 0 :
            # we are in prestart
            pass
        else:
            sail_class = self.config_['order'][self.class_index_]
            timeline = self.config_['class_timeline']
            
        num_seconds_in = int(self.tick_index_ / self.ticks_per_second_)
        # do this on whole seconds
        if (self.tick_index_ * self.ticks_per_second_) % 1.0 == 0:
            if self.music_countdown_ > 0:
                self.music_countdown_ = self.music_countdown_ - 1
                if self.music_countdown_ == 0:
                    self.horn_.stop()
            # determine if we have a new function
            for i in timeline:
                if i == num_seconds_in:
                    if timeline[i].function is not None:
                        self.timeline_function_ = timeline[i].function
                        if self.timeline_function_ == "ShowOrder": 
                            self.pause_seconds = 1
                            self.scroll_seconds = 3
                        elif self.timeline_function_ == "ShowOrderQuick": 
                            self.pause_seconds = 0
                            self.scroll_seconds = 2
                        elif self.timeline_function_ == "ClassFlagUp": 
                            self.horn_.play(timeline[i].music)
                            self.music_countdown_ = timeline[i].music_timeout
                    if timeline[i].music_timeout is not None and timeline[i].music is not None:
                        self.horn_.play(timeline[i].music)
                        self.music_countdown_ = timeline[i].music_timeout

        if self.timeline_function_ == "ShowOrder" or self.timeline_function_ == "ShowOrderQuick": 
            self.show_order_tick()
        elif self.timeline_function_ == "ClassFlagUp" or self.timeline_function_ == "PrepFlageUp" or self.timeline_function_ == "PrepFlageDown": 
            self.count_down_tick()
            # show the class flag to the right
            self.leds_.write_over_frame(sail_class['name'], 0xffffff, sail_class['color'], 30, 2)
            if self.timeline_function_ == "PrepFlageUp" and num_seconds_in % 2 == 1:
                # every odd second, show the prep flag instead of countdown
                self.show_prepflag_left()
        else: self.count_down_tick()
        self.mode_ = MODE.WAITING
        self.current_task_ = None


    def count_down_tick(self, reset_background = True):
        # tick every second
        if (self.tick_index_ * self.ticks_per_second_) % 1.0 == 0:
            self.seconds_countdown_ -= 1
            num_min = int(self.seconds_countdown_ / 60)
            seconds_remaining = self.seconds_countdown_ % 60

            # self.display_big_number(0, self.min_countdown_, True)
            # self.display_big_number(13, self.tens_seconds_countdown_, False)
            # self.display_big_number(24, self.seconds_countdown_, False)
            if reset_background:
                self.leds_.fill_color(self.background_color_)
            self.framebuf_.text(str(num_min) + ":" + str(seconds_remaining).zfill(2), 1, 1, self.fill_color_)

        
    def show_order_tick(self):
        # for each order, give 4 seconds pause, then scroll for 6?
        # determine bottom index (not the scroller), then top index, which will scroll
        # 
        bottom_index = 0
        num_seconds_in = self.show_order_tick_index / self.ticks_per_second_
        if num_seconds_in > self.pause_seconds:
            bottom_index = int((num_seconds_in - self.pause_seconds) / (self.pause_seconds + self.scroll_seconds)) + 1

        if bottom_index + 1 > len(self.config_['order']):
            return

        self.leds_.fill_color(self.config_['order'][bottom_index]['color'])
        self.leds_.fill_text(str(bottom_index + 1) + "-" + self.config_['order'][bottom_index]['name'], 1, 2, 0xffffff)

        if num_seconds_in > self.pause_seconds:
            top_index = int(num_seconds_in / (self.pause_seconds + self.scroll_seconds)) 

            # is the bottom the only thing shown?
            ticks_in_this_index = self.show_order_tick_index - ((top_index) * (self.pause_seconds + self.scroll_seconds) / self.seconds_per_tick_)
            is_paused = ticks_in_this_index < self.pause_seconds * self.ticks_per_second_
            logging.warn("is_paused " + str(is_paused) + " " + str(ticks_in_this_index))
            if not is_paused:                
                # overwrite new row with old row for shifting affect. determine how much we shift by.
                ticks_into_scrolling = self.show_order_tick_index - ((top_index) * (self.pause_seconds + self.scroll_seconds) / self.seconds_per_tick_) - (self.pause_seconds / self.seconds_per_tick_)
                offset_x = int((ticks_into_scrolling / (self.scroll_seconds * self.ticks_per_second_)) * self.framebuf_.width)

                logging.warn("frame_x " + str(self.show_order_tick_index) + " " + str(offset_x) + " " + str(ticks_into_scrolling))
                self.leds_.write_over_frame(str(top_index + 1) + "-" + self.config_['order'][top_index]['name'], 0xffffff, self.config_['order'][top_index]['color'], offset_x, 2)
