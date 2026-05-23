"""
# Wrapper program to run the Asteroids game under Badge OS.
#
# Copyright (C) 2026 Paul Fretwell - aka 'Footleg'
#
# This app launcher runs the Asteroids game on the Tufty2350 badge.
#
# This code is released under the [GPL-3.0 License](https://opensource.org/license/gpl-3.0).
#
"""

# Your apps directory on the badge
APP_DIR = "/system/apps/asteroids"

import os
import sys
# So the apps can share one copy of hardware wrapper, located in the assets folder
sys.path.append('/system/assets') 
from tufty2350 import Hardware_Wrapper
from asteroids import AsteroidsGame
# Standalone bootstrap for finding app assets
os.chdir(APP_DIR)

# Standalone bootstrap for module imports
sys.path.insert(0, APP_DIR)

# We'll use high resolution mode for this app
badge.mode(HIRES)

# The game clears it's objects by drawing over them in black before redrawing on each update, 
# so disable the Badge OS default clear here to prevent it wiping the frame on each update as
# the code depends on objects persisting on screen between frames for some features.
badge.default_clear = None

# Set the font used for text on screen
screen.font = pixel_font.load("/system/assets/fonts/bacteria.ppf")

# Called once to initialise your app.
def init():
    global display, game
    display = Hardware_Wrapper()
    
    # Create the game instance with the display
    game = AsteroidsGame(display)
    
    # Initialize the game
    game.initialize()

# Called every frame, to update the game state and the content on the screen
def update():
    game.update()

# Handle saving your app state here
def on_exit():
    pass

init()
run(update)
