# Python Games

Games written in python using a hardware abstraction architecture so they are runnable using Pygame on a computer, or on microcontrollers using MicroPython. Example hardware classes are provided for Pygame and for the Pimoroni Tufty2350 badge (https://badgewa.re).

## apps
Each directory under apps contains a game or example graphics application which can run on any of the supported hardware platforms. You can run any on them on a computer with Python and Pygame installed. (Install pygame into Python using: `pip install pygame` ). 
Then copy the directory under apps for the app you want to install onto the badge, into the apps directory on the badge. You can change the icon.png file to give your app it's own custom icon in the Badge OS menu screen.

## hardware-wrappers

This directory contains the hardware wrappers. The hardware-pygame wrapper is ready to be used by any of the apps via the 'run_app.py' launch scripts. To run an app on Badge OS, first copy the tufty2350.py file into the 'assets' directory on the badge.
