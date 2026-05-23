'''
# Tufty hardware wrapper, to enable programs to run on Tufty2350 badgeware.
# Put this file in the assets folder on the Badge OS file system.
# The Hardware_Wrapper class is passed into the constructor of your app so
# all hardware interaction (e.g. graphics drawing, button or key presses) is
# done through this hardware abstraction layer. This way the app does not need
# any hardware dependencies in the code and can run on any hardware that you
# write a suitable hardware wrapper for.
#
# Copyright (c) 2026 Paul Fretwell - aka 'Footleg'
#
# This code is released under the [MIT License](http://opensource.org/licenses/MIT).
#
# Note: The hardware abstraction framework is provided under the MIT license, but
# individual apps in this repo are licensed under GNU GENERAL PUBLIC LICENSE v3
'''

from machine import Timer, reset
from time import sleep_ms, sleep_us, ticks_diff, ticks_us, sleep

class Hardware_Wrapper:
    # Methods to wrap timing functions. Just return MicroPython utime methods
    @staticmethod
    def sleep(seconds):
        """Sleep for the given number of seconds."""
        sleep(seconds)

    @staticmethod
    def sleep_ms(milliseconds):
        """Sleep for the given number of milliseconds."""
        sleep_ms(milliseconds)

    @staticmethod
    def sleep_us(microseconds):
        """Sleep for the given number of microseconds."""
        sleep_us(microseconds)

    @staticmethod
    def ticks_ms():
        """Return the current ticks elapsed in milliseconds."""
        return ticks_us() // 1000

    @staticmethod
    def ticks_us():
        """Return the current ticks elapsed in microseconds."""
        return ticks_us()

    @staticmethod
    def ticks_diff(ticks1, ticks2):
        """Calculate the difference between two ticks values."""
        return ticks_diff(ticks1, ticks2)

    @staticmethod
    def color_from_rgb(r, g, b):
        """ Convert RGB values to a color object of the correct type for this hardware"""
        return color.rgb(r, g, b)

    # Map key constants used for control.
    # Different apps ask for control inputs for different purposes, 
    # so we have duplicate mappings of the badge buttons here to suit
    # multiple apps.
    KEY_A = BUTTON_A
    KEY_B = BUTTON_B
    KEY_C = BUTTON_C

    KEY_UP = BUTTON_UP
    KEY_DOWN = BUTTON_DOWN
    KEY_LEFT = KEY_A
    KEY_RIGHT = KEY_C

    KEY_START = KEY_B
    KEY_FIRE = KEY_A
    KEY_RUN = KEY_C


    def __init__(self):
        self.width = screen.width
        self.height = screen.height
        self.black = color.rgb(0, 0, 0)
        self.white = color.rgb(255, 255, 255)
        self.red = color.rgb(255, 0, 0)
        self.green = color.rgb(0, 255, 0)
        self.blue = color.rgb(0, 0, 255)
        self.yellow = color.rgb(255, 255, 0)

    def show(self):
        pass

    def fill(self, colour):
        screen.pen = colour
        screen.clear()

    def fill_rect(self, x, y, w, h, colour):
        screen.pen = colour
        screen.shape(shape.rectangle(x, y, w, h))

    def text(self, text, x, y, colour):
        screen.pen = colour
        screen.text(text, x, y)

    def line(self, x1, y1, x2, y2, colour):
        screen.pen = colour
        screen.shape(shape.line(x1, y1, x2, y2, 1))

    def pixel(self, x, y, colour):
        self.fill_rect(x, y, 2, 2, colour)

    def circle(self, x, y, radius, colour):
         screen.pen = colour
         screen.shape(shape.circle(int(x), int(y), max(int(radius), 1)))

    def is_key_held(self, key):
        # Check if a key is currently being held
        return badge.held(key) 

    def create_timer(self):
        return Timer()

    def reset(self):
        reset()
