"""
# Wrapper program to run the Asteroids game with pygame as a display device.
#
# Copyright (C) 2026 Paul Fretwell - aka 'Footleg'
#
# This launcher instantiates the a display device using PyGame and passes it to 
# the Asteroids game class, allowing the game to run on a computer. This allows
# the game to be developed, debugged and played on any Linux or Windows computer
# with Python and Pygame installed.
#
# Released under the [GPL-3.0 License](https://opensource.org/license/gpl-3.0).
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

from asteroids import AsteroidsGame


def main():
    """Main entry point for the game launcher."""
    # Create the display device with the resolution of your choice
    display = Hardware_Wrapper(800, 600) #(320, 240) (400, 300) (800, 600) (1600, 1000) 
    
    # Set font size for this app
    display.set_font('Arial', 28)
    
    # Create the game instance with the display
    game = AsteroidsGame(display)
    
    # Initialize the game
    game.initialize()

    sleep_time = 0.01
    
    # Main game loop
    running = True
    while running:
        # Update and render the game
        fps = game.update()

        if display.quit_requested():
            running = False
            break

        try:
            # Frame rate control
            if fps > 25:
                sleep_time += 0.001
                print(f"Sleep time: {sleep_time}")
            sleep(sleep_time)
        except Exception:
            running = False

    # Cleanup
    pygame.quit()


if __name__ == "__main__":
    main()
