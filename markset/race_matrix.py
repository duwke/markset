
import asyncio

import neopixel
import board
import adafruit_framebuf
import yaml
from enum import Enum
import time
import logging


class RaceMatrix:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, pixels, width, height, fill_color=0xff0000, background_color=0x000000):
        print("race matrix init")   
        self.pixels_ = pixels
        self.framebuf_ = adafruit_framebuf.FrameBuffer(bytearray(width * height * 3), width, height, buf_format=adafruit_framebuf.RGB888)
        self.top_framebuf_ = adafruit_framebuf.FrameBuffer(bytearray(self.framebuf_.width * self.framebuf_.height * 4), self.framebuf_.width, self.framebuf_.height, buf_format=adafruit_framebuf.RGB888)
        self.background_color_ = background_color
        self.fill_color_ = fill_color

        self.clear()
        
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

    def width(self):
        return self.framebuf_.width

    def clear(self):
        self.framebuf_.fill(self.background_color_)

    def copy_matrix_to_led(self):
        if self.pixels_ == None:
            return
        # start at top left
        for y in range(self.framebuf_.height):
            led_matrix_y = y
            for x in range(self.framebuf_.width):
                if y % 2 != 0:
                    self.pixels_[led_matrix_y * self.framebuf_.width + x] = self.framebuf_.pixel(x, y)
                else:
                    self.pixels_[led_matrix_y * self.framebuf_.width + self.framebuf_.width - x - 1] = self.framebuf_.pixel(x, y)

        self.pixels_.show()

    def fill_color(self, c):
        self.framebuf_.fill(c)

    def fill_top_color(self, color):
        self.framebuf_.fill_rect(0, 0, self.framebuf_.width, int(self.framebuf_.height/2), color)
    
    def fill_right_color(self, color):
        self.framebuf_.fill_rect(int(self.framebuf_.width/2), 0, self.framebuf_.width, self.framebuf_.height, color)
    
    def fill_bottom_color(self, color):
        self.framebuf_.fill_rect(0, int(self.framebuf_.height/2), self.framebuf_.width, self.framebuf_.height, color)
    
    def show_prepflag_left(self):
        for y in range(self.framebuf_.height):
            for x in range(int(self.framebuf_.width / 2)):
                if x >= 8 and x < int(self.framebuf_.width / 2) - 8 and y >= 2 and y < self.framebuf_.height - 2:
                    self.framebuf_.pixel(x, y, 0xFFFFFF)
                else:
                    self.framebuf_.pixel(x, y, 0x0000FF)

    
    ''' x from left, y from top, c = color ffffff '''
    def fill_text(self, text, x, y, c):
        self.framebuf_.text(text, x, y, c)
    def fill_text_top_right(self, text, c=0xffffff):
        self.framebuf_.text(text, int(self.framebuf_.width / 2) + 2, 2, c)

    def fill_big_text(self, text, x, y, c):
        self.framebuf_.fill(self.background_color_)  # otherwise left and top row are missed
        self.top_framebuf_.fill(self.background_color_)
        self.top_framebuf_.text(text, x, y, c)
        # at the end of the frame, make each pixel 4, doubling the size of the text
        for y in range(int(self.framebuf_.height / 2)):  
            for x in range(self.framebuf_.width) :  
                self.framebuf_.pixel(x * 2 + 1, y * 2 + 1, self.top_framebuf_.pixel(x, y))
                self.framebuf_.pixel(x * 2 + 2, y * 2 + 1, self.top_framebuf_.pixel(x, y))
                self.framebuf_.pixel(x * 2 + 1, y * 2 + 2, self.top_framebuf_.pixel(x, y))
                self.framebuf_.pixel(x * 2 + 2, y * 2 + 2, self.top_framebuf_.pixel(x, y))
        

    ''' this is for the shifting affect.  create a frame over the current'''
    def write_over_frame(self, text, c, background_color, x_offset, y_offset):
        self.top_framebuf_.fill(background_color)
        self.top_framebuf_.text(text, 1, y_offset, c)
        
        #just write to bottom half
        for y in range(int(self.framebuf_.height / 2), self.framebuf_.height):  
            for x in range(self.framebuf_.width) :  
                self.framebuf_.pixel(x + x_offset, y, self.top_framebuf_.pixel(x, y))
                
    def display_big_number(self, offset, num, debug):
        if self.framebuf_.height < 20:
            raise Exception('numbers are currently 20 wide and 20 long')
        #just write to top half
        for i in range(self.framebuf_.height):
            bit_row = self.matrix_nums[num][i]
            # the numbers are currently 20 leds wide
            for j in range(19, -1, -1):
                # git bit is reversed
                # print(str(str(j) +  " " + str(bit_row) + " " + str(1 << j)))
                if self.get_bit(bit_row, j) == 1:
                    self.framebuf_.pixel(offset + (19 - j), i, self.fill_color_)
                else:
                    self.framebuf_.pixel(offset + (19 - j), i, self.background_color_)

    def cat_in_hat(self):
        for y in range(self.framebuf_.height):
            for x in range(int(self.framebuf_.width)):
                if x % 6 < 3:
                    self.framebuf_.pixel(x, y, 0xFF0000)
                else:
                    self.framebuf_.pixel(x, y, 0xFFFFFF)

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


        
        