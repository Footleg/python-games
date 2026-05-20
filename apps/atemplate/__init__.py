'''
# Template application project showing how to run an app using the hardware
# abstraction layer on Badge OS. Copy this file along with the application code 
# graphics_app.py and icon.png file into a directory named 'atemplate' under the 
# apps folder on the badge. You also need to copy the tufty2350.py hardware 
# wrapper file into the assets folder on the Badge OS file system.
#
# The Hardware_Wrapper class is passed into the constructor of the app so that
# all hardware interaction (e.g. graphics drawing, button or key presses) is
# done through the hardware abstraction layer. This way the app does not need
# any hardware dependencies in the code and can run on any hardware that you
# write a suitable hardware wrapper for.
#
# Copyright (c) 2026 Paul Fretwell - aka 'Footleg'
#
# This code is released under the [MIT License](http://opensource.org/licenses/MIT).
#
# Note: The hardware abstraction framework and this template app are provided under 
# the MIT license, but other apps in this repo are licensed under the GPL-3.0 License.
'''

# Your apps directory on the badge
APP_DIR = "/system/apps/atemplate"

import os
import sys
sys.path.append('/system/assets')
from tufty2350 import Hardware_Wrapper
import graphics_app

# Standalone bootstrap for finding app assets
os.chdir(APP_DIR)

# Standalone bootstrap for module imports
sys.path.insert(0, APP_DIR)

# We'll use high resolution mode for this app
badge.mode(HIRES)

# setup for our app objects
screen.font = rom_font.sins

# Called once to initialise your app.
def init():
    global display, app
    
    # Create the display device (hardware)
    display = Hardware_Wrapper()

    # Create the app instance with the display
    app = graphics_app.demo_app(display)
    
    # Initialize the app
    app.initialize()

# Called every frame, update and render as you see fit!
def update():
    app.update()

# Handle saving your app state here
def on_exit():
    pass

# Initialise and run app on Badge OS
init()
run(update)
