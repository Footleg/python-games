"""
# Wrapper program to run the Gravity Simulation app with pygame as a display device.
#
# Copyright (C) 2026 Paul Fretwell - aka 'Footleg'
#
# This launcher instantiates the a display device using PyGame and passes it to 
# the appliation class, allowing the app to run on a computer. This allows
# the app to be developed, debugged and played on any Linux or Windows computer
# with Python and Pygame installed.
#
# This code is released under the [GPL-3.0 License](https://opensource.org/license/gpl-3.0).
#
"""

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
from gravity_simulation_app import GravitySimulationApp

def main():
    """Main entry point for the game launcher."""
    # Create the display device
    display = Hardware_Wrapper(1600, 1000) # (320, 240) (800, 600)
    
    # Create the game instance with the display
    game = GravitySimulationApp(display, display.width // 100, 1, 1024)
    
    # Initialize the game
    game.initialize()

    sleep_time = 0.01
    
    # Main game loop
    running = True
    while running:
        # Update and render the game
        game.update()

        if display.quit_requested():
            running = False
            break

        try:
            # Frame rate control
            sleep(sleep_time)
        except Exception:
            running = False

    # Cleanup
    pygame.quit()


if __name__ == "__main__":
    main()

