
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
                [0b0001111000],
                [0b0011001100],
                [0b0110000110],
                [0b1100000011],
                [0b1100000011],
                [0b1100000011],
                [0b1100000011],
                [0b0110000110],
                [0b0011001100],
                [0b0001111000],
            ],[
                [0b0001110000],
                [0b0011110000],
                [0b0110110000],
                [0b0000110000],
                [0b0000110000],
                [0b0000110000],
                [0b0000110000],
                [0b0000110000],
                [0b0000110000],
                [0b1111111111],
            ],[
                [0b0001111000],
                [0b0110000110],
                [0b1100000011],
                [0b0000000011],
                [0b0000001100],
                [0b0000110000],
                [0b0011000000],
                [0b1100000000],
                [0b1100000000],
                [0b1111111111],
            ],[
                [0b0011111100],
                [0b1100000110],
                [0b0000000011],
                [0b0000000110],
                [0b0000111000],
                [0b0000000110],
                [0b0000000011],
                [0b0000000011],
                [0b1100000110],
                [0b0011111000],
            ],[
                [0b0000000110],
                [0b0000011110],
                [0b0001100110],
                [0b0110000110],
                [0b1100000110],
                [0b1111111111],
                [0b0000000110],
                [0b0000000110],
                [0b0000000110],
                [0b0000000110],
            ],[
                [0b1111111111],
                [0b1100000000],
                [0b1100000000],
                [0b1100000000],
                [0b1111111100],
                [0b0000000110],
                [0b0000000011],
                [0b0000000011],
                [0b1100000110],
                [0b0011111100],
            ],[
                [0b0000111000],
                [0b0011000000],
                [0b0110000000],
                [0b110000000],
                [0b1111111100],
                [0b1100000110],
                [0b1100000011],
                [0b0110000110],
                [0b0011001100],
                [0b0001111000],
            ],[
                [0b1111111110],
                [0b0000000011],
                [0b0000000011],
                [0b0000000110],
                [0b0000001100],
                [0b0000011000],
                [0b0000110000],
                [0b0001100000],
                [0b0011000000],
                [0b0110000000],
            ],[
                [0b0001111000],
                [0b0110000110],
                [0b1100000011],
                [0b0110000110],
                [0b0001111000],
                [0b0110000110],
                [0b1100000011],
                [0b1100000011],
                [0b0110000110],
                [0b0011111100],
            ],[
                [0b0001111000],
                [0b0110000110],
                [0b1100000011],
                [0b0110000011],
                [0b0001111111],
                [0b0000000011],
                [0b0000000011],
                [0b0000000011],
                [0b0000000110],
                [0b0001111000],
            ]
        ]

        self.matrix_ = []
        for i in range(self.rows_):
            for j in range(self.columns_):
                self.matrix_.append(background_color)
        self.update_ui_cb_(self.matrix_)

    def BeginTimer(self, num_minutes):

        self.min_countdown_ = num_minutes
        self.tens_seconds_countdown_ = 0
        self.seconds_countdown_ = 0

        self.current_task_ = uasyncio.get_event_loop().create_task(self._timer)

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

        self.DisplayNumber(0, self.min_countdown_)
        self.DisplayNumber(11, self.tens_seconds_countdown_)
        self.DisplayNumber(21, self.seconds_countdown_)

        self.update_ui_cb_(self.matrix_)
        

    def DisplayBigNumber(self, offset, num):
        if self.rows_ < 10:
            raise Exception('numbers are currently 10 wide and 10 long')
        for i in range(self.rows):
            bit_row = self.matrix_nums[num][i]
            start_index = (self.columns_ * i) + offset
            # the numbers are currently 10 leds wide
            for j in range(10, 1, -1):
                # git bit is reversed
                if self.get_bit(bit_row, j) == True:
                    self.matrix_[start_index + (10 - j)] = self.fill_color_
                else:
                    self.matrix_[start_index + (10 - j)] = self.background_color_
                    

    def get_bit(value, bit_index):
        return value & (1 << bit_index)


        
        