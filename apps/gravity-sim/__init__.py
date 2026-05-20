"""
# Wrapper program to run the Gravity Simulation app under Badge OS.
#
# Copyright (C) 2026 Paul Fretwell - aka 'Footleg'
#
# This app launcher runs the Gravity Simulation app on the Tufty2350 badge.
#
# This code is released under the [GPL-3.0 License](https://opensource.org/license/gpl-3.0).
#
"""

# Your apps directory on the badge
APP_DIR = "/system/apps/gravity-sim"

import os
import sys
# So the apps can share one copy of hardware wrapper, located in the assets folder
sys.path.append('/system/assets') 
from tufty2350 import Hardware_Wrapper
from gravity_simulation_app import GravitySimulationApp

# Standalone bootstrap for finding app assets
os.chdir(APP_DIR)

# Standalone bootstrap for module imports
sys.path.insert(0, APP_DIR)

# We'll use high resolution mode for this app
badge.mode(HIRES)

# The app clears the frame to black before redrawing on each update, so disable the 
# Badge OS default clear here or it clears the screen to black twice, halving the frame rate.
badge.default_clear = None

# Set the font to use for text in this app
screen.font = pixel_font.load("/system/assets/fonts/absolute.ppf")

# Called once to initialise your app.
def init():
    global display, game
    display = Hardware_Wrapper()
    
    # Create the game instance with the display
    game = GravitySimulationApp(display)
    
    # Initialize the game
    game.initialize()


# Called every frame, update and render as you see fit!
def update():
    game.update()


# Handle saving your app state here
def on_exit():
    pass

# Initialise and run app on Badge OS
init()
run(update)
