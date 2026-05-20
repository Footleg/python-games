# Python Games

Games written in python using a hardware abstraction architecture so they are runnable using Pygame on a computer, or on microcontrollers using MicroPython. Example hardware wrapper classes are provided for Pygame and for the Pimoroni Tufty2350 badge (<https://badgewa.re>).

## apps

Each directory under apps contains a game or example graphics application which can run on any of the supported hardware platforms. You can run any on them on a computer with Python and Pygame installed. (Install Pygame into Python using: `pip install pygame` ). Just run the run_app.py file in the directory for the app you want to run under Pygame.

To run on the Tufty2350 badge, copy the directory under apps into the apps directory on the badge for the app you want to install. You can change the icon.png file to give your app its own custom icon in the Badge OS menu screen. See below for how to deploy the relevant hardware wrapper.

## hardware-wrappers

This directory contains the hardware wrappers. The Hardware_Wrapper class is passed into the constructor of your app so all hardware interaction (e.g. graphics drawing, button or key presses) is done through the hardware abstraction layer. This way the app does not need any hardware dependencies in the code and can run on any hardware that you write a suitable hardware wrapper for. The hardware wrapper provides a common interface graphics methods, including how to define colours, and button or keyboard input. The wrapper also provides a set of methods for timing functions and an implementation of the Timer class found in Micropython, so that apps can run on both full Python or on Micropython without requiring any code changes.
The hardware-pygame wrapper is ready to be used by any of the apps via their `run_app.py` launch scripts. Just clone this git repo and launch the run_app.py script in any of the app folders.
To run an app on Badge OS, first copy the `tufty2350.py` file into the 'assets' directory on the badge, then deploy the app files into the 'apps' directory on the badge and it should appear as a new icon on the Badge OS menu screen.
