"""
# Gravity simulation
#
# This program simulates spheres in a 2-D space with attractive or repelling forces.
# This is a python conversion of the original C++ implementation in my RGB Animations
# project (https://github.com/Footleg/RGBMatrixAnimations)
# 
# This implementation was written as a reusable animation class where a hardware
# wrapper class is passed in, so it can be used with any device.
# 
# Copyright (C) 2026 Paul Fretwell - aka 'Footleg'
# 
# Released under the [GPL-3.0 License](https://opensource.org/license/gpl-3.0).
"""

import random
import math

class Ball:
    def __init__(self, x, y, r, dx, dy, colour):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.colour = colour


class GravitySimulationApp():
    def __init__(self, hardware, max_radius=20, initial_balls=1, max_balls=128):
        self.display = hardware
        self.max_radius = max_radius
        self.force_power = 10.0
        self.max_balls = max_balls # Limit maximum number of balls to prevent memory issues
        self.mode = 1  # 0 = bounce, 1 = force
        self.minX = 0
        self.minY = 0
        self.maxX = self.display.width - 1
        self.maxY = self.display.height - 1
        self.balls: list[Ball] = []
        self.initial_balls = initial_balls
        self.debug_ticks = self.display.ticks_ms() # Tracks how long debug messages are displayed
        self.last_add_ticks = self.debug_ticks     # Prevents multiple ball adds on button press
        self.last_mode_ticks = self.debug_ticks    # Prevents modes rapidly cycling when button held
        self.btn_delay_ms = 160 # ms time between acting on button held detections for repeating actions
        self.debug = False # Flag to determine whether debug messaging is shown or not
        self.gticks = 0
        self.fps = 0
        self.frames = 0

    def initialize(self):
        self.show_messages()
        for _ in range(self.initial_balls):
            self.add_ball()

    def handle_input(self):
        if self.display.is_key_held(self.display.KEY_C):
            self.reset()
        else:
            if self.display.is_key_held(self.display.KEY_A):
                # Toggle mode if suitable delay since last mode change
                self.show_messages()
                now = self.display.ticks_ms()
                if self.display.ticks_diff(now, self.last_mode_ticks) >= self.btn_delay_ms:
                    self.last_mode_ticks = now
                    if self.mode == 0:
                        self.mode = 1
                    else:
                        self.mode = 0

            if self.display.is_key_held(self.display.KEY_B):
                # Add a ball if suitable delay since last add
                now = self.display.ticks_ms()
                if self.display.ticks_diff(now, self.last_add_ticks) >= self.btn_delay_ms:
                    self.show_messages()
                    self.add_ball()
                    self.last_add_ticks = now

            if self.display.is_key_held(self.display.KEY_UP) or self.display.is_key_held(self.display.KEY_DOWN):
                self.show_messages()
                increment = 5
                abs_force = abs(self.force_power)
                if abs_force < 1:
                    increment = 0.01
                elif abs_force < 2:
                    increment = 0.05
                elif abs_force < 100:
                    increment = 0.025 * abs_force
                    
                if self.display.is_key_held(self.display.KEY_DOWN):
                    increment = -increment
                # Increase force power
                self.force_power += increment
        
    def show_messages(self):
        # Turn on debug messaging
        self.debug = True
        self.debug_ticks = self.display.ticks_ms()

    def update(self):
        self.display.fill(self.display.black)
        self.update_simulation()
        if self.debug:
            self.draw_debug()
        if self.display.ticks_diff(self.display.ticks_ms(), self.debug_ticks) > 5000:
            self.debug = False
        self.display.show()
        self.frames += 1
        if self.frames > 16:
            self.fps = 1_000_000 * self.frames // self.display.ticks_diff(self.display.ticks_us(), self.gticks)
            self.gticks = self.display.ticks_us()
            self.frames = 0
        self.handle_input()

    def update_simulation(self):
        for i, ball in enumerate(self.balls):
            ball.x += ball.dx
            ball.y += ball.dy

            for j in range(i):
                other = self.balls[j]
                sep_x = other.x - ball.x
                sep_y = other.y - ball.y
                sep = math.sqrt(sep_x*sep_x + sep_y*sep_y)

                if sep <= 0.0:
                    continue

                ax = 0.0
                ay = 0.0
                rd = ball.r + other.r

                if sep < rd:
                    if self.mode == 0 or sep < rd / 4.0:
                        ax = sep_x
                        ay = sep_y
                elif self.mode == 1:
                    force = -self.force_power / (sep * sep)
                    ax = force * sep_x / sep
                    ay = force * sep_y / sep

                pre_power = math.sqrt(ball.dx*ball.dx + ball.dy*ball.dy) + math.sqrt(other.dx*other.dx + other.dy*other.dy)
                ball.dx -= ax * other.r
                ball.dy -= ay * other.r
                other.dx += ax * ball.r
                other.dy += ay * ball.r

                post_power = math.sqrt(ball.dx*ball.dx + ball.dy*ball.dy) + math.sqrt(other.dx*other.dx + other.dy*other.dy)
                if post_power > 0.0:
                    scale = pre_power / post_power
                    ball.dx *= scale
                    ball.dy *= scale
                    other.dx *= scale
                    other.dy *= scale

            if (ball.x - ball.r) < self.minX:
                ball.dx *= -1
                ball.x = self.minX + ball.r
            if (ball.x + ball.r) >= self.maxX:
                ball.dx *= -1
                ball.x = self.maxX - ball.r
            if (ball.y - ball.r) < self.minY:
                ball.dy *= -1
                ball.y = self.minY + ball.r
            if (ball.y + ball.r) >= self.maxY:
                ball.dy *= -1
                ball.y = self.maxY - ball.r

        self.draw_balls()

    def draw_balls(self):
        for ball in self.balls:
            self.display.circle(ball.x, ball.y, ball.r, ball.colour)

    def draw_debug(self):
        mode_label = "Bounce" if self.mode == 0 else "Forces"
        self.display.text(f"Balls: {len(self.balls)}  Mode: {mode_label}, Force: {self.force_power:.2f}, fps: {self.fps}", 10, 10, self.display.red)
        self.display.text("A=toggle mode  B=add ball  C=reset", 10, 30, self.display.yellow)
        self.display.text("Up/Down=change force strength", 10, 50, self.display.yellow)

    def add_ball(self):
        if len(self.balls) >= self.max_balls:
            return
        self.balls.append(self.create_ball())

    def create_ball(self):
        x = random.uniform(self.minX + 10, self.maxX - 10)
        y = random.uniform(self.minY + 10, self.maxY - 10)
        radius = random.randint(2, self.max_radius)
        dx = random.uniform(-2.5, 2.5)
        dy = random.uniform(-2.5, 2.5)

        rgb = [0, 0, 0]
        while sum(rgb) < 192:
            rgb = [random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)]

        return Ball(x=x, y=y, r=radius, dx=dx, dy=dy, colour=self.display.color_from_rgb(rgb[0], rgb[1] ,rgb[2]))

    def reset(self):
        self.balls = []
        self.display.sleep_ms(200) # Pause to prevent rapid repeated resets on button press
        self.initialize()
