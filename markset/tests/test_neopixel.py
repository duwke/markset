import board
import neopixel
import digitalio
# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D21
num_pixels = 600
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=.2, auto_write=False, pixel_order=ORDER
)

pixels.fill((0, 0, 0))
pixels[2] = (0, 66, 66)
pixels[4] = (255, 0, 66)
pixels.show()

# led = digitalio.DigitalInOut(board.D21)
# led.direction = digitalio.Direction.OUTPUT
# led.value = 1