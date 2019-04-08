from picamera.array import PiRGBArray  # Works better with numpy and opencv
from picamera import PiCamera  # Picamera functions
import time
import numpy as np
import cv2  # First step to sentient computers
import argparse
import board  # For neopixel ring lights
import neopixel  # Let there be light

#-----setting up argparse

parser = argparse.ArgumentParser()
parser.add_argument("-res", "--resolution", nargs='*', default=[1920,1080],
                    type=int, help="the native resolution of the viewing screen, enter width,\
                    then height seperated by space\
                    (default set to 1920*1080)")
group = parser.add_mutually_exclusive_group()
group.add_argument("-full", "--fullscreen", help="runs the stream in fullscreen bordeless mode",
                    action="store_true")
group.add_argument("-half", "--halfscreen", help="runs the stream with window taking up half of the screen",
                    action="store_true")
group.add_argument("-c", "--custom", help="runs the stream with window resolution input, needs -x  and -y input",
                   action="store_true")
parser.add_argument("-x", nargs='?', type=int, help="the width of the window")
parser.add_argument("-y", nargs='?', type=int, help="the height of the window")
args = parser.parse_args()

#-----setup

def placeholder( x ):
    ''' Needed for trackbar functinality'''
    pass
def brightness_update():
    ''' Updates the brightness value for functions'''
    brightness = cv2.getTrackbarPos( "Brightness", "Video Stream" )
    return( brightness )
##def light_ring(brightness, pixel_pin, num_pixels, pixel_order):
##
##    brightness = int(brightness)
##    pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2,
##                           pixel_order=ORDER)
##    pixels.fill((0, 0, 0, brightness))
##    pixels.show()

# Initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640,480))

# Allow the camera to warmup
time.sleep(0.1)

# Sets up LED Ring pixels
pixel_pin = board.D18
num_pixels = 16
ORDER = neopixel.RGBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2,
                           pixel_order=ORDER)


# Sets the native screen resolution, default 1920*1080
native_screen_res = (args.resolution[0], args.resolution[1])

# Creates window for video depending on flag
if args.fullscreen:
    cv2.namedWindow("Video Stream", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Video Stream", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN )
    cv2.createTrackbar( "Brightness", "Video Stream", 128, 255, placeholder )
elif args.halfscreen:
    cv2.namedWindow("Video Stream", cv2.WINDOW_KEEPRATIO)
    cv2.resizeWindow("Video Stream", native_screen_res[0]/2, native_screen_res[1])
    cv2.moveWindow("Video Stream", 0, 0)
    cv2.createTrackbar( "Brightness", "Video Stream", 128, 255, placeholder )
elif args.custom:
    cv2.namedWindow("Video Stream", cv2.WINDOW_AUTOSIZE)
    cv2.resizeWindow("Video Stream", args.x, args.y)
    cv2.createTrackbar( "Brightness", "Video Stream", 128, 255, placeholder )
else:
    cv2.namedWindow("Video Stream", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Video Stream", 640, 480)
    cv2.createTrackbar( "Brightness", "Video Stream", 128, 255, placeholder )


    
    

# Captures frames from the camera
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    # Grabs the frame then initializes
    image = frame.array
    if args.fullscreen:
        # Scales image to higher resolution
        image = cv2.resize(image, native_screen_res, cv2.INTER_AREA)
    elif args.halfscreen:
        # Scales the image to half the native width keeping aspect ratio
        scale = (native_screen_res[0]/2)/image.shape[0]
        image = cv2.resize(image, (native_screen_res[0]/2, image.shape[1]*scale), cv2.INTER_AREA)
    elif args.custom:
        # Scales image to set resolution
        image = cv2.resize(image, (args.x, args.y ), cv2.INTER_AREA)
    
    brightness = brightness_update()
    pixels.fill((0, 0, 0, brightness))
    pixels.show()
    # Show the frame
    cv2.imshow("Video Stream", image)
    key = cv2.waitKey(1) & 0xFF
    # Clear the stream for next frame
    rawCapture.truncate(0)
    # Press keystroke "q" to break loop and stream
    if key == ord("q"):
        pixels.fill((0, 0, 0, 0))
        pixels.show()

        break
    # In case caps lock is on
    if key == ord("Q"):
        pixels.fill((0, 0, 0, 0))
        pixels.show()

        break

cv2.destroyAllWindows()

