
import asyncio
from distutils.command.config import config

import race_matrix
import board
import adafruit_framebuf
import yaml
from enum import Enum
import time
import logging
import sys, os
from datetime import datetime


class MODE(Enum):
    WAITING = 0
    COUNTDOWN = 1
    SHOW_ORDER = 2
    RACING = 3
    MESSAGE = 4 # show a string
    DELAY = 5
class RaceManager:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, race_matrix, horn):
        print("race matrix init")   
        self.leds_ = race_matrix
        self.horn_ = horn
        self.seconds_countdown_ = 0
        self.current_task_ = None
        self.mode_ = MODE.WAITING
        self.start_time_ = None
        self.ticks_per_second_ = 6 
        self.tick_index_ = 0 # the number of _timer ticks.  Keep this so we always tick the correct number of times, even if we get behind.
        self.show_order_tick_index = 0 # same as above for SHOW_ORDER, but can be reset for RACING to show order during
        self.ticks_total_ = 0 # for each mode, we set the number of expected ticks at the desired frequency
        self.config_ = None
        self.pause_seconds = 1 #scrolling
        self.scroll_seconds = 3
        self.music_countdown_ = 0 # start music.  set to x, and once it gets to 0, we call stop.
        self.class_index_ = -1 # -1 is prestart
        self.timeline_function_ = ""
        self.shutdown_ = False
        self.message_ = ""
        self.message_ticks_per_character_ = 6 #characters are 6 pixels wide
        self.message_pause_secs_ = 3
        with open("markset/config.yaml", "r") as stream:
            try:
                self.config_ = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def shutdown(self):
        self.shutdown_ = True

    def begin_racing(self, class_index = -1):
        # set mode
        logging.warn("begin_racing")

        #reload just in case
        with open("markset/config.yaml", "r") as stream:
            try:
                self.config_ = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.mode_ = MODE.RACING
        self.class_index_ = class_index
        prestart_length = list(self.config_["prestart_timeline"][0].keys())[0] # get first time, this is overall length

        logging.warn("prestart_length " + str(prestart_length))
        self.begin_timer_(prestart_length)

    def begin_show_order(self, class_index = 0):
        # set mode
        # todo: use class_index
        logging.warn("begin_show_order")
        self.mode_ = MODE.SHOW_ORDER
        num_seconds = (self.pause_seconds * self.scroll_seconds) * (len(self.config_['order']) + 1)
        self.show_order_tick_index = 0
        self.begin_timer_(num_seconds)
        
    def begin_countdown(self, seconds):
        logging.warn("begin_countdown")
        # set mode
        self.mode_ = MODE.COUNTDOWN
        self.begin_timer_(seconds)

    def begin_message(self, message):
        logging.warn("begin_message " + str(message))
        # set mode
        self.message_ = message
        seconds = ((len(message) * self.message_ticks_per_character_) / self.ticks_per_second_) + self.message_pause_secs_
        self.mode_ = MODE.MESSAGE
        self.begin_timer_(seconds)

    # Delay for x minutes ending at the :00 gps time, then start 
    def begin_delay(self, minutes = 1):
        logging.warn("delay")
        # set mode
        self.mode_ = MODE.DELAY
        now = datetime.now()
        seconds = now.second + (minutes) * 60  # it will never be less than one minute
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
        while self.tick_index_ <  self.ticks_total_ and not self.shutdown_:
            if self.mode_ == MODE.COUNTDOWN:
                self.count_down_tick()
            if self.mode_ == MODE.SHOW_ORDER:
                self.show_order_tick()
            if self.mode_ == MODE.RACING:
                self.racing_tick()
            if self.mode_ == MODE.MESSAGE:
                self.message_tick()
            if self.mode_ == MODE.DELAY:
                self.delay_tick()

            self.tick_index_ += 1
            self.show_order_tick_index += 1
            if (self.tick_index_ % self.ticks_per_second_) == 0:
                self.seconds_countdown_ -= 1

            self.leds_.copy_matrix_to_led()

            duration = time.time() - self.start_time_
            num_ticks = int(duration * self.ticks_per_second_)
            if num_ticks <= self.tick_index_:
                # just sleep enough to get to the next tick.
                mill_seconds_til_next_tick = ((self.tick_index_ + 1) / self.ticks_per_second_) - duration
                logging.warn("ticks " + str(num_ticks) + "/" + str(self.ticks_total_))
                await asyncio.sleep(mill_seconds_til_next_tick) 
            else:
                logging.warn("catchup ticks " + str(duration * self.ticks_per_second_) + " > " + str(self.tick_index_))

        logging.warn("stop task")
        self.leds_.clear()
        self.leds_.copy_matrix_to_led()
        self.current_task_ = None
        if self.mode_ == MODE.COUNTDOWN:
            self.begin_show_order()


    def racing_tick(self):
        try:
            timeline = self.config_['prestart_timeline']
            sail_class = None
            if self.class_index_ < 0 :
                # we are in prestart
                pass
            else:
                sail_class = self.config_['order'][self.class_index_]
                timeline = self.config_['class_timeline']
                
            
            # play seems to take half a second to start.  We need this more precise for the horns
            if self.tick_index_ % self.ticks_per_second_ == int(self.ticks_per_second_ / 2):
                for i in timeline:
                    timeline_seconds = list(i.keys())[0]
                    timeline_obj = i[timeline_seconds]
                    if timeline_obj.__contains__("music"):
                        if timeline_seconds + 1 == self.seconds_countdown_:
                            logging.warn("Start music " + timeline_obj["music"])
                            self.horn_.play(timeline_obj["music"])
                            if timeline_obj.__contains__("music_timeout"):
                                self.music_countdown_ = timeline_obj["music_timeout"]
                            else: self.music_countdown_ = 2

            # do this on whole seconds
            if self.tick_index_ % self.ticks_per_second_ == 0:
                logging.warn("whole second " + str(self.seconds_countdown_))
                if self.music_countdown_ > 0:
                    self.music_countdown_ = self.music_countdown_ - 1

                    logging.warn("music countdown " + str(self.music_countdown_))
                    if self.music_countdown_ == 0:
                        self.horn_.stop()
                # determine if we have a new function
                for i in timeline:
                    timeline_seconds = list(i.keys())[0]
                    timeline_obj = i[timeline_seconds]

                    if timeline_seconds == self.seconds_countdown_:
                        if timeline_obj.__contains__("function"):
                            logging.warn("Start function " + timeline_obj["function"])
                            self.timeline_function_ = timeline_obj["function"]
                            if self.timeline_function_ == "ShowOrder": 
                                self.pause_seconds = 1
                                self.scroll_seconds = 3
                                self.show_order_tick_index = 0
                            elif self.timeline_function_ == "ShowOrderQuick": 
                                self.pause_seconds = 1
                                self.scroll_seconds = 0
                                # only show the current order remaining
                                self.show_order_tick_index = self.ticks_per_second_ * self.class_index_
                            elif self.timeline_function_ == "ClassTunes": 
                                self.horn_.play(sail_class["music"])
                                self.music_countdown_ = 59

            #ticks
            if self.timeline_function_ == "ShowOrder" or self.timeline_function_ == "ShowOrderQuick": 
                self.show_order_tick()
            elif self.timeline_function_ == "ClassTunes" or self.timeline_function_ == "ClassFlagUp" or self.timeline_function_ == "PrepFlageUp" or self.timeline_function_ == "PrepFlageDown": 
                self.count_down_tick(shift_left=True, color=0xFF0000)
                logging.warn("classflag")
                # show the class flag to the right
                self.leds_.write_over_frame(sail_class['name'], 0xffffff, sail_class['color'], 30, 2)
                if self.timeline_function_ == "PrepFlageUp" and self.seconds_countdown_ % 2 == 1:
                    # every odd second, show the prep flag instead of countdown
                    logging.warn("PrepFlageUp " + str(self.seconds_countdown_ % 2))
                    self.leds_.show_prepflag_left()
            elif self.class_index_ == -1:
                self.count_down_tick(0x00ff00)
            else: self.count_down_tick(0xff0000)

            # go to next class
            if  self.tick_index_ == self.ticks_total_ - 1 and self.class_index_ + 1 < len(self.config_["class_timeline"]) :
                self.class_index_ = self.class_index_ + 1
                sail_class = self.config_['order'][self.class_index_]
                logging.warn("changing class " + str(sail_class))
                self.seconds_countdown_ = list(self.config_["class_timeline"][0].keys())[0] #largest time in class_timeline
                self.begin_timer_(self.seconds_countdown_)
            elif self.tick_index_ == self.ticks_total_ - 1:
                self.begin_message("http://GBCA.org  Wednesday Night Racing")
        except Exception as inst:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(inst))

    def count_down_tick(self, reset_background = True, shift_left = False, color = 0x00FF00):
        # tick every second
        if (self.tick_index_ % self.ticks_per_second_) == 0:
            num_min = int(self.seconds_countdown_ / 60)
            seconds_remaining = self.seconds_countdown_ % 60

            # self.display_big_number(0, self.min_countdown_, True)
            # self.display_big_number(13, self.tens_seconds_countdown_, False)
            # self.display_big_number(24, self.seconds_countdown_, False)
            if reset_background:
                self.leds_.clear()

            left_index = 15
            if shift_left:
                left_index = 1
            self.leds_.fill_text(str(num_min) + ":" + str(seconds_remaining).zfill(2), left_index, 2, color)

        
    def show_order_tick(self):
        # for each order, give 4 seconds pause, then scroll for 6?
        # determine bottom index (not the scroller), then top index, which will scroll
        # 
        bottom_index = 0
        num_seconds_in = self.show_order_tick_index / self.ticks_per_second_
        if num_seconds_in > self.pause_seconds:
            bottom_index = int((num_seconds_in - self.pause_seconds) / (self.pause_seconds + self.scroll_seconds)) + 1

        if bottom_index + 1 > len(self.config_['order']):
            logging.warn("order complete")
            self.timeline_function_ = "Countdown" 
            return

        self.leds_.fill_color(self.config_['order'][bottom_index]['color'])
        self.leds_.fill_text(str(bottom_index + 1) + "-" + self.config_['order'][bottom_index]['name'], 1, 2, 0xffffff)

        if num_seconds_in > self.pause_seconds:
            top_index = int(num_seconds_in / (self.pause_seconds + self.scroll_seconds)) 

            # is the bottom the only thing shown?
            ticks_in_this_index = self.show_order_tick_index - ((top_index) * (self.pause_seconds + self.scroll_seconds) * self.ticks_per_second_)
            is_paused = ticks_in_this_index < self.pause_seconds * self.ticks_per_second_
            logging.warn("is_paused " + str(is_paused) + " " + str(ticks_in_this_index))
            if not is_paused:                
                # overwrite new row with old row for shifting affect. determine how much we shift by.
                ticks_into_scrolling = self.show_order_tick_index - ((top_index) * (self.pause_seconds + self.scroll_seconds)  * self.ticks_per_second_) - (self.pause_seconds * self.ticks_per_second_)
                offset_x = int((ticks_into_scrolling / (self.scroll_seconds * self.ticks_per_second_)) * self.leds_.width())

                logging.warn("frame_x " + str(self.show_order_tick_index) + " " + str(offset_x) + " " + str(ticks_into_scrolling))
                self.leds_.write_over_frame(str(top_index + 1) + "-" + self.config_['order'][top_index]['name'], 0xffffff, self.config_['order'][top_index]['color'], offset_x, 2)

    def message_tick(self):
        num_seconds_in = self.tick_index_ / self.ticks_per_second_
        logging.warn("message_tick "+ str(num_seconds_in) + " " + str(self.message_pause_secs_))
        self.leds_.clear()
        if(num_seconds_in < self.message_pause_secs_):
            logging.warn("message_tick1")
            self.leds_.fill_text(self.message_, 1, 2, 0xffffff)
        else:
            index = self.tick_index_ - (self.ticks_per_second_ * self.message_pause_secs_) * (self.message_ticks_per_character_ / 6) # six pixels per character
            logging.warn("message_tick2 " + self.message_ + " " + str(index))
            self.leds_.fill_text(self.message_, -int(index), 2, 0xffffff)

    
    def delay_tick(self):
        num_seconds_in = self.tick_index_ / self.ticks_per_second_

        if self.tick_index_ == 0:
            self.horn_.play("ambulance.mp3")
            self.music_countdown_ = 10

        self.leds_.clear()

        if (num_seconds_in % 1) >= .5:
            self.leds_.cat_in_hat() 
        else:
            num_min = int(self.seconds_countdown_ / 60)
            seconds_remaining = self.seconds_countdown_ % 60
            if (num_seconds_in % 2) >= 1:
                # show flag
                sail_class = self.config_['order'][self.class_index_]
                self.leds_.write_over_frame("next" + sail_class['name'], 0xffffff, sail_class['color'], 0, 2)

            else:
                # countdown
                self.leds_.fill_text(str(num_min) + ":" + str(seconds_remaining).zfill(2), 15, 2, 0xFF0000)


        
        