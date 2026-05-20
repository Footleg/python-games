'''
# Template application project showing how to run an app using the hardware
# abstraction layer using Pygame on a computer. This file should launch the app
# on any computer which has python and pygame installed.
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

import pygame
from time import sleep
import os
import sys

# Get the directory of the current script to build the path to the hardware wrapper
# This allows it to be shared across all the apps
script_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.join(script_dir, "../../hardware-wrappers")
sys.path.append(os.path.abspath(target_path))
from hardware_pygame import Hardware_Wrapper
from graphics_app import demo_app

def main():
    """Main entry point for the app launcher."""
    # Create the display device at the resolution of your desired window size here
    display = Hardware_Wrapper(320, 240) # (800, 600) (1600, 1000)
    
    # Create the app instance with the display
    app = demo_app(display)
    
    # Initialize the app
    app.initialize()
    
    # Main app loop
    running = True
    while running:
        # Update and render the app
        app.update()

        if display.quit_requested():
            running = False
            break

        try:
            # Frame rate control
            sleep(0.1)
        except Exception:
            running = False

    # Cleanup
    pygame.quit()


if __name__ == "__main__":
    main()

