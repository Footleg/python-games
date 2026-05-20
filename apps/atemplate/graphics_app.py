'''
# Template application project showing how to write a graphics app for any hardware
# using a hardware wrapper. This app tests button or key press inputs and drawing
# methods to render a UI. All interaction with hardware (inputs and outputs) is
# handled through a hardware wrapper class passed into the constructor of the app. 
# This way the app does not need any hardware dependencies in the code and can run 
# on any hardware that you write a suitable hardware wrapper for. In order to run on
# both full Python on a computer, and on Micropython on microcontroller boards, the
# hardware wrapper also needs to provide timer and timing functions which are not
# supported with the same syntax in both environments.
#
# Copyright (c) 2026 Paul Fretwell - aka 'Footleg'
#
# This code is released under the [MIT License](http://opensource.org/licenses/MIT).
#
# Note: The hardware abstraction framework and this template app are provided under 
# the MIT license, but other apps in this repo are licensed under the GPL-3.0 License.
'''

class demo_app:
    def __init__(self, hardware):
        # Store hardware instance
        self.display = hardware

        # Initialise app state variables
        self.circle_x = 150
        self.last_press = 0 # Track time since last action taken on button press

    # Put any application initialisation code here which needs to be done after 
    # the class constructor has finished.
    def initialize(self):
        pass

    # Example of using keyboard input
    def handle_input(self):

        if self.display.is_key_held(self.display.KEY_START):
            print(f"Start key is being held at {self.display.ticks_ms()}!")
            self.display.text(f"Start key is being held at {self.display.ticks_ms()}!", 10, 110, self.display.white)

        if self.display.is_key_held(self.display.KEY_A):
            # Check if enough time passed since last acting on press
            if self.display.ticks_diff(self.display.ticks_ms(),self.last_press) > 100:
                self.circle_x += 5
                if self.circle_x > 320:
                    self.circle_x = 10
                print(f"Circle at {self.circle_x},75")
                self.last_press = self.display.ticks_ms()

    # Called every frame, update and render as you see fit!
    def update(self):
        self.display.fill(self.display.black)
        self.display.text("Hello World!", 10, 10, self.display.white)

        self.display.line(10, 30, 200, 30, self.display.red)

        self.display.fill_rect(10, 50, 100, 50, self.display.color_from_rgb(255, 198, 50))

        # Circle should align with rectangle and be the same height
        self.display.circle(self.circle_x, 75, 25, self.display.color_from_rgb(125, 60, 50))

        for i in range(10):
            self.display.pixel(10*i, 180, self.display.green)

        self.handle_input()
        self.display.show()
