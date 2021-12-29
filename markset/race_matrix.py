
import uasyncio



class RaceMatrix:
### a generic class for displaying 10x60 matrix.  Consumed by web and led display.


    def __init__(self, rows, columns, update_ui_cb, fill_color=(254, 254, 254), background_color=(0,0,0)):
        self.rows_ = rows
        self.columns_ = columns
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

        self.matrix_ = []
        for i in range(self.rows_):
            for j in range(self.columns_):
                self.matrix_.append(background_color)
        self.update_ui_cb_(self.matrix_)

        # FrameBuffer needs 2 bytes for every RGB565 pixel
        #self.fbuf = framebuf.FrameBuffer(bytearray(rows * columns * 2), columns, rows, framebuf.RGB565)
        #self.fbuf.fill(0)

    def BeginTimer(self, num_minutes):

        self.min_countdown_ = num_minutes
        self.tens_seconds_countdown_ = 0
        self.seconds_countdown_ = 0
        if self.current_task_ is None:
            self.current_task_ = uasyncio.get_event_loop().create_task(self._timer())

    async def _timer(self):
        while self.seconds_countdown_ >= 0 and self.tens_seconds_countdown_ >= 0 and self.min_countdown_ >= 0:
            self.CountDown()
            await uasyncio.sleep(1) # need to sleep to next full time second

    def CountDown(self):
        self.seconds_countdown_ -= 1
        if(self.seconds_countdown_ < 0):
            self.seconds_countdown_ = 9
            self.tens_seconds_countdown_ -= 1
        if(self.tens_seconds_countdown_ < 0):
            self.tens_seconds_countdown_ = 5
            self.min_countdown_ -= 1

        self.DisplayBigNumber(0, self.min_countdown_, True)
        self.DisplayBigNumber(13, self.tens_seconds_countdown_, False)
        self.DisplayBigNumber(24, self.seconds_countdown_, False)

        self.update_ui_cb_(self.matrix_)

        # index = y+colunas*x
        # pixel = dataArray[index]
        # #invert byte order
        # pixel = ((dataArray[index]&0xFF)<<8)|(dataArray[index]>>8)
        # #separa as cores
        # R = pixel&0b1111100000000000
        # G = pixel&0b0000011111100000
        # B = pixel&0b0000000000011111
        # #shift para a posição correta
        # a[x,y,0] = R>>8
        # a[x,y,1] = G>>3
        # a[x,y,2] = B<<3
        

    def DisplayBigNumber(self, offset, num, debug):
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
                    self.matrix_[start_index + (9 - j)] = self.fill_color_
                else:
                    self.matrix_[start_index + (9 - j)] = self.background_color_

    def get_bit(self, value, bit_index):
        # print(str(value) + " " + str(1 << bit_index) + " " + str(value & (1 << bit_index)))
        return value & (1 << bit_index) == (1 << bit_index)


        
        