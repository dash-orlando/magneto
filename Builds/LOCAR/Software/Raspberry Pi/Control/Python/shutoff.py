import board
import neopixel

pixel_pin = board.D18
num_pixels = 16
ORDER = neopixel.RGBW

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2,
                           pixel_order=ORDER)

#shutoff lights
pixels.fill((0, 0, 0, 0))
