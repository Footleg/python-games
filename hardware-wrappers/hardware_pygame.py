'''
# Pygame virtual hardware wrapper, to enable programs to be developed, tested 
# and run on a computer.
# 
# App runners import this directly from the repo, so it does not need deploying
# beyond just cloning the code from github.
# 
# The Hardware_Wrapper class is passed into the constructor of your app so
# all hardware interaction (e.g. graphics drawing, button or key presses) is
# done through this hardware abstraction layer. This way the app does not need
# any hardware dependencies in the code and can run on any hardware that you
# write a suitable hardware wrapper for. This module also provides a Python 
# implementation of the Timer class found in MicroPython, so that apps which use
# a timer to trigger a callback function can run on a computer. 
#
# Copyright (c) 2026 Paul Fretwell - aka 'Footleg'
#
# This code is released under the [MIT License](http://opensource.org/licenses/MIT).
#
# Note: The hardware abstraction framework is provided under the MIT license, but
# individual apps in this repo are licensed under GNU GENERAL PUBLIC LICENSE v3
'''

import pygame
import pygame.freetype
from time import sleep, time
import threading

class Hardware_Wrapper:
    # Methods to wrap timing functions to implement equivalent to MicroPython utime methods
    @staticmethod
    def sleep(seconds):
        """Sleep for the given number of seconds."""
        sleep(seconds)

    @staticmethod
    def sleep_ms(milliseconds):
        """Sleep for the given number of milliseconds."""
        sleep(milliseconds / 1000.0)

    @staticmethod
    def sleep_us(microseconds):
        """Sleep for the given number of microseconds."""
        sleep(microseconds / 1000000.0)

    @staticmethod
    def ticks_ms():
        """Return the current time in milliseconds."""
        return int(time() * 1000)

    @staticmethod
    def ticks_us():
        """Return the current time in microseconds."""
        return int(time() * 1000000)

    @staticmethod
    def ticks_diff(ticks1, ticks2):
        """Calculate the difference between two ticks values."""
        return ticks1 - ticks2

    @staticmethod
    def color_from_rgb(r, g, b):
        """ Convert RGB values to a color object of the correct type for this hardware"""
        return [r, g, b]


    # Map key constants used for control. You can map as many as your hardware
    # provides here, but apps will only use the ones they reference in their code.
    KEY_A = pygame.K_a
    KEY_B = pygame.K_b
    KEY_C = pygame.K_c
    KEY_UP = pygame.K_UP
    KEY_DOWN = pygame.K_DOWN

    # Additional purpose focused key aliases
    KEY_START = pygame.K_RETURN
    KEY_LEFT = pygame.K_LEFT
    KEY_RIGHT = pygame.K_RIGHT
    KEY_FIRE = pygame.K_SPACE
    KEY_RUN = pygame.K_RCTRL

    def __init__(self, w, h):
        pygame.init()
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tufty2350 Badge Emulator")
        self.font = pygame.freetype.SysFont('Arial', 12)
        self.black = [0, 0, 0]
        self.white = [255, 255, 255]
        self.red = [255, 0, 0]
        self.green = [0, 255, 0]
        self.blue = [0, 0, 255]
        self.cyan = [0, 255, 255]
        self.magenta = [255, 0, 255]
        self.yellow = [255, 255, 0]
        
        self.keys_held = {}  # Track keys being held
        self.should_quit = False

    def set_font(self, name, size):
        self.font = pygame.freetype.SysFont(name, size)

    def fill(self, color):
        self.screen.fill(color)

    def text(self, text, x, y, color):
        self.font.render_to(self.screen, (x, y), text, color)

    def line(self, x1, y1, x2, y2, color):
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2))

    def fill_rect(self, x, y, width, height, color):
        pygame.draw.rect(self.screen, color, (x, y, width, height))

    def pixel(self, x, y, color):
        self.screen.set_at((int(x), int(y)), color)

    def circle(self, x, y, radius, color, filled=True):
        if filled:
            pygame.draw.circle(self.screen, color, (int(x), int(y)), max(int(radius), 1))
        else:
            pygame.draw.circle(self.screen, color, (int(x), int(y)), max(int(radius), 1), width=1)

    def show(self):
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.should_quit = True
            elif event.type == pygame.KEYDOWN:
                self.keys_held[event.key] = True
            elif event.type == pygame.KEYUP:
                self.keys_held[event.key] = False

    def quit_requested(self):
        return self.should_quit

    def is_key_held(self, key):
        # Check if a key is currently being held
        return self.keys_held.get(key, False)

    def reset(self):
        self.fill(self.black)

    def create_timer(self):
        return TIMER()

class TIMER:
    # Define timer modes as constants
    ONE_SHOT = 0
    PERIODIC = 1

    def __init__(self):
        self._timer = None
        self._callback = None
        self._args = None

    def init(self, period, mode, callback=None, arg=None):
        """
        Initialize the timer.

        Args:
            period (int): The period in milliseconds.
            mode (int): The timer mode (e.g., Timer.ONE_SHOT or Timer.PERIODIC).
            callback (function): The callback function to execute.
            arg (optional): Additional argument to pass to the callback.
        """
        self.deinit() # Reset in case it already fired before being reinitialized
        self._period = period / 1000.0  # Convert to seconds
        self._mode = mode
        self._callback = callback
        self._args = arg if arg is not None else ()

        self.start()

    def deinit(self):
        """Deinitialize the timer."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def start(self):
        """Start the timer."""
        if self._timer is not None:
            self._timer.cancel()
        else:
            if self._mode == TIMER.ONE_SHOT:
                self._timer = threading.Timer(self._period, self._execute_callback)
            elif self._mode ==  TIMER.PERIODIC:
                self._timer = threading.Timer(self._period, self._periodic_callback)
            else:
                raise ValueError("Invalid timer mode")

            # Start the timer
            self._timer.start()

    def _execute_callback(self):
        """Execute the callback once."""
        if self._callback is not None:
            self._callback(self._args)

    def _periodic_callback(self):
        """Execute the callback periodically."""
        if self._callback is not None:
            self._callback(self._args)
        self.start()  # Restart the timer for periodic execution

