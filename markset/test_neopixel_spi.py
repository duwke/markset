import board
import neopixel_spi as neopixel
# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
spi = board.SPI()

# The number of NeoPixels
num_pixels = 600

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB


pixels = neopixel.NeoPixel_SPI(
    spi, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER
)

pixels.fill((0, 0, 0))
pixels[3] = (0, 66, 66)
pixels[5] = (255, 0, 0)
pixels.show()