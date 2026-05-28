""" 
# A hardware agnostic game implementation by Footleg, based on game code published under a 
# GPL-3.0 license at https://github.com/samneggs/pi-pico
#
# Compared to the original code, this port refactors the game into a reusable class
# where a hardware wrapper class is passed in, so it can be used with any device. 
# The game class knows nothing about the hardware it is running on. The original code
# controlled the game loops so animation sequences could run in their own loops. In this
# version the game clock is controlled by the application outside the game class, so all
# animations need to render just one frame before returning control to the host program.
# This requires state to be stored in the class between frames. The game has also been
# rewritten to scale to different sizes of display. 
# 
# Derived from game code by github user samneggs published in 2021.
#
# This version copyright (C) 2026 Paul Fretwell - aka 'Footleg'
# 
# Released under the [GPL-3.0 License](https://opensource.org/license/gpl-3.0).
""" 
from math import sin,cos,radians,sqrt
from random import randint
import array

class Point():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.ax = 0
        self.ay = 0
        self.c = 0
        self.exp = 0
        self.deg = 0
        self.active = 0
        
class Obj_point():
    def __init__(self):
        self.x = 0
        self.y = 0

class Vector_Object():
    """ Used for all vector objects (ship, asteroids, letters for game messages) """
    def __init__(self, ptdeg, ptrad, pts, tumble, x, y, size, display):
        self.x = x # 230000 
        self.y = y # 125000 
        self.ax = 0 #randint(-40,40)*10 #10 # accel x
        self.ay = 0 #randint(-40,40)*10 # accel y 
        self.deg = 0                 # degrees obj is pointing
        self.size = size             # size of obj
        self.scale = 1.0             # scale of obj
        self.coll = self.size        # collision h and w (converted to mean radius using calc_coll later)
        self.exp = 0                 # explode progression
        self.damage = True           # ship can take damage
        self.pt = []                 # active points
        self.ptrad = ptrad           # radius - points
        self.ptdeg = ptdeg           # degrees - points
        self.pts = pts               # number of points
        self.tumble = tumble         # degress added for tumbling
        self.active = True           # show on screen, move...
        self.back_colour = display.black
        self.colour = display.white #0x008A
        self.fps = 25                # Controls game animations so initialise to target fps
        self.active_exhaust = 0

    def calc_coll(self, scale=1.0):
        """ Sets collision radius to mean of object points radius """
        mean_rad = 0
        for i in range(len(self.ptrad)-1):
            mean_rad += self.ptrad[i];
        mean_rad = int(self.size * self.scale * scale * mean_rad) // (len(self.ptrad)-1)
        self.coll = mean_rad

class Score():
    def __init__(self):
        self.value = 0
        self.digits = ['0','1','2','3','4','5','6','7','8','9']
        self.places = 0
        self.lives = 0 # Let the game set this
        self.show = False
 
class GAME_MODE():
    TITLE = 1
    PLAY = 2
    GAME_OVER = 3

# Static data for UI elements (shared across instances)
rotn = [-3,-2,-1,1,2,3] # tumble, removed zero

# Letter definitions for title
let_deg = []
let_rad = []

# Score digit definitions
score_deg = []
score_rad = []
scoring = [0,100,50,30,20,15,10,4,2,1] # points scored for each asteroid size

# Objects are defined in terms of radial coordinates by an array of angles and an array of distances from the centre
let_deg.append([54,270,126,90,54])                      # A
let_rad.append([17,18,17,4,17])
let_deg.append([306,270,234,54,90,126])                 # S
let_rad.append([17,18,17,17,18,17])
let_deg.append( [234, 306, 270, 90] )                   # T   
let_rad.append( [17, 17, 12, 14] )
let_deg.append( [306, 234, 0, 126, 54] )                # E
let_rad.append( [17, 17, 0, 17, 17] )
let_deg.append( [0, 306, 270, 234, 126, 191, 0, 60] )   # R
let_rad.append( [0, 17, 16, 17, 17, 10, 0, 16] )       
let_deg.append( [306, 270, 234, 126, 90, 54, 306] )     # O
let_rad.append( [17, 16, 17, 17, 16, 17, 17] )         
let_deg.append( [306, 270, 234, 270, 90, 54, 90, 126] ) # I
let_rad.append( [17, 16, 17, 14, 14, 17, 16, 17] )
let_deg.append( [234, 270, 0, 90, 126, 234] )           # D
let_rad.append( [17, 14, 10, 14, 17, 17] )
let_deg.append([306,270,234,54,90,126])                 # S
let_rad.append([17,18,17,17,18,17])
let_deg.append( [126, 234, 0, 306, 54] )                # M
let_rad.append( [17, 17, 0, 17, 17] )
let_deg.append( [234, 90, 306] )                        # V
let_rad.append( [17, 18, 17] )

score_deg.append( [306, 270, 234, 126, 90, 54, 306] )    # 0
score_rad.append( [17, 18, 17, 17, 18, 17, 17] )
score_deg.append( [90, 270, 234] )                       # 1
score_rad.append( [18, 18, 17] )                        
score_deg.append( [234, 270, 306, 126, 90, 54] )         # 2
score_rad.append( [17, 18, 17, 17, 18, 17] )            
score_deg.append( [234, 270, 306, 0, 54, 90, 126] )      # 3
score_rad.append( [17, 18, 17, 0, 17, 18, 17] )         
score_deg.append( [90, 270, 180, 0] )                    # 4
score_rad.append( [18, 18, 18, 0] )
score_deg.append( [306, 270, 234, 180, 0, 54, 90, 126] ) # 5
score_rad.append( [17, 18, 17, 10, 10, 17, 18, 17] )
score_deg.append( [306, 270, 234, 126, 90, 54, 0, 180] ) # 6
score_rad.append( [17, 18, 17, 17, 18, 17, 0, 10] ) 
score_deg.append( [234, 270, 306, 90] )                  # 7
score_rad.append( [17, 18, 17, 18] )
score_deg.append( [270, 306, 126, 90, 54, 234, 270] )    # 8
score_rad.append( [18, 17, 17, 18, 17, 17, 18] )
score_deg.append( [306, 0, 234, 270, 306, 90] )          # 9
score_rad.append( [17, 0, 17, 18, 17, 18] )


class AsteroidsGame:
    """ Main game class that encapsulates all asteroids game logic.

        Hardware wrapper is passed in so the game does not need to 
        contain any hardware specific code. It just calls the methods
        on the hardware object and that handles interfacing with the
        actual hardware the game is running on.
    """
    
    def __init__(self, hardware):
        # Create hardware instances
        self.display = hardware
        self.timer = hardware.create_timer()

        # Screen Constants
        self.MAXSCREEN_X = int(hardware.width - 1)
        self.MAXSCREEN_Y = int(hardware.height - 1)
        self.SCALE       = int(1000)
        self.MAX_X = self.MAXSCREEN_X * self.SCALE # Calc. once as used a lot
        self.MAX_Y = self.MAXSCREEN_Y * self.SCALE # Calc. once as used a lot

        # Capture key constants used by the game
        self.KEY_LEFT = hardware.KEY_LEFT 
        self.KEY_RIGHT = hardware.KEY_RIGHT
        self.KEY_UP = hardware.KEY_UP 
        self.KEY_DOWN = hardware.KEY_DOWN
        self.KEY_START = hardware.KEY_START
        self.KEY_FIRE = hardware.KEY_FIRE
        self.KEY_RUN = hardware.KEY_RUN
        
        # Game parameters affecting difficulty. Some depend on screen area
        self.asteroid_max_size = int(sqrt(hardware.width / 30))
        self.initial_asteroids = 1 + hardware.width // 250
        self.asteroid_inc = max(self.initial_asteroids // 2, 1)
        self.max_asteroids = (self.initial_asteroids + self.asteroid_inc * 10) * self.asteroid_max_size # Max 10 levels
        self.max_missiles = hardware.width // 40
        self.hitbox_debug = False
        self.hitbox_scale = 0.9 # 1.0 is exact mean object size

        # Game state
        self.game_mode = GAME_MODE.TITLE
        self.title_frame = 0
        self.big_score_frame = 0
        self.score = Score()

        # Single objects
        self.ship = self._init_obj([0, 140, 220, 0], [3, 3, 3, 3], 8, 0, self.MAX_X // 2, self.MAX_Y // 2, 3 * self.SCALE)
        self.ship.coll = self.ship.size * 5 # Sets size of shield collision boundary
        self.ship.colour = self.display.green
        
        # Game object lists
        self.bullets = []              # missile point list
        self.rocks = []                # asteroid point list
        self.expPnts = []              # explode point list
        self.exhausty = []             # exhaust list
        self.asteroid = []             # big asteroids
        self.titleLetts = []           # title letters
        self.over_list = []            # game over text
        self.score_list = []           # score digit objects
        
        # Lookup tables
        self.isin = array.array('i', range(0, 361))
        self.icos = array.array('i', range(0, 361))
        
        # Initialize colour shades
        self.white_shades = []
        self.red_shades = []
        self.green_shades = []
        self.yellow_shades = []
        self._init_shades()
        
        # Game counters and state
        self.gticks = 0
        self.rfire = 0 # Counts frames since a shot was last fired
        self.demo = 0                  # 1 = demo mode
        self.num_asteroids = self.initial_asteroids    # number of asteroids to start level
        self.active_asteroids = self.num_asteroids
        self.asteroid_count = 0
    
    def _init_shades(self):
        """Initialize colour shade arrays."""
        for i in range(0, 32):
            shade = i * 8
            self.white_shades.append(self.display.color_from_rgb(shade, shade, shade))
            self.red_shades.append(self.display.color_from_rgb(shade, 0, 0))
            self.green_shades.append(self.display.color_from_rgb(0, shade, 0))
            self.yellow_shades.append(self.display.color_from_rgb(shade, shade, 0))
    
    def _perimeter(self, obj, xmax, ymax):
        """Return x,y on the perimeter of x,y."""
        x = randint(0, xmax)
        y = randint(0, ymax)
        p = randint(0, xmax * 2 + ymax * 2)
        if p < ymax:
            x = 0
        elif p > xmax * 2 + ymax:
            x = xmax
        elif p < xmax + ymax:
            y = 0
        else:
            y = ymax
        obj.x = x
        obj.y = y
    
    def _init_isin(self):
        """Initialize integer sin lookup table."""
        for i in range(0, 361):
            self.isin[i] = int(sin(radians(i)) * 10000)
    
    def _init_icos(self):
        """Initialize integer cos lookup table."""
        for i in range(0, 361):
            self.icos[i] = int(cos(radians(i)) * 10000)
    
    def _init_title_letts(self):
        """Initialize title letter objects."""
        for i in range(0, 9):
            self.titleLetts.append(self._init_obj(let_deg[i], let_rad[i], len(let_deg[i] * 2), 0, 0, 0, self.SCALE))
            self.titleLetts[i].ax = 0
            self.titleLetts[i].ay = 0
            self.titleLetts[i].size = 0
            self.titleLetts[i].back_colour = self.display.red
    
    def _init_game_over(self):
        """Initialize game over text objects."""
        self.over_list.append(self._init_obj(score_deg[6], score_rad[6], len(score_deg[6] * 2), 0, 0, 0, 0))  # G
        self.over_list.append(self._init_obj(let_deg[0], let_rad[0], len(let_deg[0] * 2), 0, 0, 0, 0))        # A
        self.over_list.append(self._init_obj(let_deg[9], let_rad[9], len(let_deg[9] * 2), 0, 0, 0, 0))        # M
        self.over_list.append(self._init_obj(let_deg[3], let_rad[3], len(let_deg[3] * 2), 0, 0, 0, 0))        # E
        self.over_list.append(self._init_obj(let_deg[5], let_rad[5], len(let_deg[5] * 2), 0, 0, 0, 0))        # O
        self.over_list.append(self._init_obj(let_deg[10], let_rad[10], len(let_deg[10] * 2), 0, 0, 0, 0))     # V
        self.over_list.append(self._init_obj(let_deg[3], let_rad[3], len(let_deg[3] * 2), 0, 0, 0, 0))        # E
        self.over_list.append(self._init_obj(let_deg[4], let_rad[4], len(let_deg[4] * 2), 0, 0, 0, 0))        # R
    
    def _show_title(self, objs):
        """ Animated title screen update frame. """
        if self.title_frame == 0:
            if self.game_mode == GAME_MODE.GAME_OVER:
                self.display.fill(self.display.black)
            self.title_pos_x = self.MAX_X // 2
            self.title_pos_y = self.MAX_Y // 8
            self.y_inc = self.MAX_Y // 6000         # 70
            self.size_inc = self.MAX_X // 32000     # 10
            self.max_title_size = self.MAX_X // 400 # 800
            self.lett_exp_idx = 0
            self.lett_exp_next = 0
        elif self.title_frame < 20: # 20 frames after letters stop enlarging
            self._animate_star_zoom(self.title_pos_y + self.max_title_size * 60)
            
            # Move letters to the left of screen centre each per frame. 
            # Amount is proportional to number of letters so the title stays in the centre.
            self.title_pos_x -= self.MAX_X * len(objs) // 2540 
            offset_x = 0
            still_growing = False
            for i in objs:
                # Enlarge letters until they reach max size
                if i.size < self.max_title_size:
                    self.title_pos_y += self.y_inc
                    i.size += self.size_inc
                    i.x = self.title_pos_x + (offset_x * i.size * 32)
                    i.y = self.title_pos_y + i.size * 60
                    i.back_colour = self.red_shades[26 * i.size // self.max_title_size]
                    still_growing = True
                else:
                    # Stop enlarging letters
                    i.tumble = 0
                    
                self._draw_object(i, False)
                offset_x += 1
            
            if still_growing:
                # Take off frame count as letters are still growing
                self.title_frame -= 1
        elif self.lett_exp_idx < len(objs):
            # Letters still to explode
            i = objs[self.lett_exp_idx]

            # Need to prep letters for explode first.
            if self.lett_exp_idx == self.lett_exp_next:
                # Prep this letter for explode
                i.exp = 0
                self._init_explode(i, 50, 1)
                self.lett_exp_next += 1
                # Wipe letter out
                i.size = 0
                self._draw_object(i, False)
            else:
                # Iterate explosion one frame
                if i.exp < 10:
                    self._explode()
                    i.exp += 1
                else:
                    self._explode_cleanup()
                    if self.lett_exp_idx == len(objs) - 1:
                        if self.game_mode == GAME_MODE.TITLE:
                            # Last letter to explode, so wipe big score and display start message
                            self.display.fill_rect(self.MAXSCREEN_X * 2 // 10, self.MAXSCREEN_Y * 9 // 16, 
                                                   self.MAXSCREEN_X * 6 // 10, self.MAXSCREEN_Y * 5 // 16, self.display.black)
                            self.display.text("Press Start", self.MAXSCREEN_X // 3, self.MAXSCREEN_Y * 5 // 8, self.display.white)
                        else:
                            # Game Over sequence ends, show score
                            self._show_big_score()
                            self.big_score_frame += 1
                            
                    # Set next letter to explode index after all the checks above.
                    self.lett_exp_idx = self.lett_exp_next
        elif self.big_score_frame > 0:
            # Show big score for 50 frames after Game Over before returning to title screen
            self.big_score_frame += 1
            self._animate_star_zoom(self.title_pos_y + self.max_title_size * 60)
            if self.big_score_frame > 50:
                self.title_frame = -1 # So it gets incremented to zero by next frame update
                self.big_score_frame = 0 # So title sequence does not re-enter this block
                self.game_mode = GAME_MODE.TITLE
        else:
            # Idling on title screen, show star zoom animation
            self._animate_star_zoom(self.title_pos_y + self.max_title_size * 60)

        self.title_frame += 1
        if self.display.is_key_held(self.KEY_START):
            # Set mode to PLAY and reset game
            self.game_mode = GAME_MODE.PLAY
            self._reset_game()

    def _init_big_score(self):
        """Initialize big score display objects."""
        for i in range(0, 10):
            self.score_list.append(self._init_obj(score_deg[i], score_rad[i], len(score_deg[i] * 2), 0, 0, 8 * self.SCALE, self.SCALE))
            self.score_list[i].y = self.MAX_Y * 7 // 10
            self.score_list[i].ax = 0
            self.score_list[i].ay = 0
            self.score_list[i].back_colour = self.display.white
            self.score_list[i].colour = self.display.white
    
    def _show_small_score(self, colour):
        """Show small fast score using text."""
        # Blank area behind text, then draw each digit
        xpos = self.MAXSCREEN_X // 5
        self.display.fill_rect(xpos - self.score.places + 2, 2, self.score.places + 12, 26, self.display.black)
        num = self.score.value
        self.score.places = 0
        while num > 0:
            self.display.text(self.score.digits[num % 10], xpos, 5, colour)
            num //= 10
            xpos -= 14
            self.score.places += 12
    
    def _show_big_score(self):
        """Show large custom score."""
        self.score.show = True
        self.display.fill_rect(self.MAXSCREEN_X * 2 // 10, self.MAXSCREEN_Y * 9 // 16, 
                               self.MAXSCREEN_X * 6 // 10, self.MAXSCREEN_Y * 5 // 16, self.display.black)
        num = self.score.value
        places = 0
        while num > 0:
            digit = num % 10
            self.score_list[digit].x = self.MAX_X * 21 // 32 - places
            self._draw_object(self.score_list[digit], False)
            num //= 10
            places += 30 * self.SCALE

        self.score.show = False
    
    def _draw_lives_remaining(self):
        # Uses the letter A from the GAMEOVER letters list as a life indicator
        self.over_list[1].x = self.MAX_X - self.SCALE * 12
        # Draw lives in a loop, 'clearing' to blue to wipe themselves out on each move
        # which stamps a copy of the marker onto the screen
        self.over_list[1].back_colour = self.display.black # Black for first draw so old position is erased
        for i in range(0, self.score.lives):
            self.over_list[1].x -= self.SCALE * 20
            self._draw_object(self.over_list[1], False)
            # Set back colour to match front so that it acts as a stamp as marker is drawn next
            self.over_list[1].back_colour = self.over_list[1].colour

    def _game_over(self):
        """Handle game over state."""
        self.over_list[1].colour = self.display.white # Reset A to white as it was used as lives marker
        for i in self.over_list:
            i.size = 0
        self.title_frame = 0
        self.big_score_frame = 0
        self.game_mode = GAME_MODE.GAME_OVER

    def _reset_game(self):
        """Reset the game state"""
        self.score.value = 0
        self.score.places = 0
        self.score.lives = 3 # Initial number of lives
        self.num_asteroids = self.initial_asteroids    # number of asteroids to start level
        self._reset_asteroids() # This sets asteroid_count
        self._init_stars() # Stop stars motion if points have been used for explosions
        self.score.show = False
        # Set up letter A from GAMEOVER to act as a lives indicator
        self.over_list[1].size = self.SCALE * 8 // 10
        self.over_list[1].y = self.SCALE * 20 #30000
        self.over_list[1].colour = self.display.blue
        # Reset title letters for next title sequence
        for i in self.titleLetts:
            i.size = 0
            i.back_colour = self.display.red
        # Reset ship
        self._new_ship()

        # Clear screen ready for new game
        self.display.fill(self.display.black)
    
    def _init_obj(self, ptdeg, ptrad, pts, tumble, x, y, size):
        """Create a game object."""
        obj = Vector_Object(ptdeg, ptrad, pts, tumble, x, y, size, self.display)
        for i in range(0, obj.pts):
            obj.pt.append(Obj_point())
        return obj
    
    def _init_asteroids(self):
        """Create asteroids list one time."""
        for j in range(0, self.max_asteroids):
            degs = [0]
            angle = randint(0, 30) + 45
            while angle < 360:
                degs.append(angle)
                angle += randint(0, 30) + 45
            if degs[len(degs)-1] > 320:
                degs[len(degs)-1] = 0
            else:
                degs.append(0)
            self.asteroid.append(self._init_obj(degs,
                                                [14] + [randint(12, 17) for _ in range(len(degs) - 2)] + [14],
                                                len(degs)*2, rotn[randint(0, 5)], 0, 0, 3 * self.SCALE + 1))
            self.asteroid[j].scale = 0.5
            self._perimeter(self.asteroid[j], self.MAX_X, self.MAX_Y)
            self.asteroid[j].ax = randint(-40, 40) * 40
            self.asteroid[j].ay = randint(-40, 40) * 40
            if j >= self.num_asteroids:
                self.asteroid[j].active = False
    
    def _reset_asteroids(self):
        """Reset asteroids."""
        # Deactivate all asteroids
        for i in self.asteroid:
            i.active = False
        # Activate and initialise the new set for the level
        for i in range(0, self.num_asteroids):
            self.asteroid[i].active = True
            self._perimeter(self.asteroid[i], self.MAX_X, self.MAX_Y)
            self.asteroid[i].size = self.SCALE * self.asteroid_max_size + 1
            self.asteroid[i].calc_coll(self.hitbox_scale)
            self.asteroid[i].tumble = rotn[randint(0, 5)]
            self.asteroid[i].exp = 0
            self.asteroid[i].ax = randint(-40, 40) * 20
            self.asteroid[i].ay = randint(-40, 40) * 20
        self.asteroid_count = self.num_asteroids
        self.active_asteroids = self.num_asteroids
    
    def _new_ship(self):
        """Reset ship to start position."""
        self.ship.exp = 0
        self.ship.x = self.MAX_X // 2
        self.ship.y = self.MAX_Y // 2
        self.ship.ax = 0
        self.ship.ay = 0
        self.ship.size = 3 * self.SCALE
        self.ship.damage = False
        self.timer.init(mode=self.timer.ONE_SHOT, period=2000, callback=self._no_damage)
    
    def _init_missiles(self):
        """Create missiles pool."""
        for i in range(0, self.max_missiles):
            self.bullets.append(Point())
    
    def _init_explosion(self):
        """Create explosion particle pool one time."""
        for i in range(0, self.MAXSCREEN_X // 3):
            self.expPnts.append(Point())
        for i in range(0, 50):
            self.exhausty.append(Point())
    
    def _draw_line(self, x1, y1, x2, y2, colour):
        """Draw a line, scaled to screen co-ordinates."""
        self.display.line(x1 // self.SCALE, y1 // self.SCALE, x2 // self.SCALE, y2 // self.SCALE, colour)
    
    def _draw_circle(self, x1, y1, r, colour):
        """Draw a circle, scaled to screen co-ordinates."""
        self.display.circle(x1 // self.SCALE, y1 // self.SCALE, r // self.SCALE, colour, False)
    
    def _draw_point(self, x, y, colour):
        """Draw a pixel, scaled to screen co-ordinates."""
        self.display.pixel(int(x // self.SCALE), int(y // self.SCALE), colour)
    
    def _draw_object_lines(self, obj, hitbox, colour):
        wrap_x_min = False
        wrap_y_min = False
        wrap_x_max = False
        wrap_y_max = False
        drawHitbox = hitbox and obj.exp < 1
        col_main = colour
        col_x_min = colour
        col_y_min = colour
        col_x_max = colour
        col_y_max = colour
        col_xy_wrap = colour
        if drawHitbox:
            if colour != self.display.black:
                col_main = self.display.red
                col_x_min = self.display.magenta
                col_y_min = self.display.yellow
                col_x_max = self.display.cyan
                col_y_max = self.display.blue
                col_xy_wrap = self.display.green
            self._draw_circle(obj.x, obj.y, obj.coll, col_main)
        
        # Draw copy if wrapping over screen boundary
        if obj.x - obj.coll < 0:
            wrap_x_min = True
            if drawHitbox:
                self._draw_circle(obj.x + self.MAX_X, obj.y, obj.coll, col_x_min)
        elif obj.x + obj.coll > self.MAX_X - 2:
            wrap_x_max = True
            if drawHitbox:
                self._draw_circle(obj.x - self.MAX_X, obj.y, obj.coll, col_x_max)
        if obj.y - obj.coll < 0:
            wrap_y_min = True
            if drawHitbox:
                self._draw_circle(obj.x, obj.y + self.MAX_Y, obj.coll, col_y_min)
        elif obj.y + obj.coll > self.MAX_Y - 2:
            wrap_y_max = True
            if drawHitbox:
                self._draw_circle(obj.x, obj.y - self.MAX_Y, obj.coll, col_y_max)

        if drawHitbox:
            # Consider corner cases also
            if wrap_x_min and wrap_y_min:
                self._draw_circle(obj.x + self.MAX_X, obj.y + self.MAX_Y, obj.coll, col_xy_wrap)
            elif wrap_x_min and wrap_y_max:
                self._draw_circle(obj.x + self.MAX_X, obj.y - self.MAX_Y, obj.coll, col_xy_wrap)
            elif wrap_x_max and wrap_y_min:
                self._draw_circle(obj.x - self.MAX_X, obj.y + self.MAX_Y, obj.coll, col_xy_wrap)
            elif wrap_x_max and wrap_y_max:
                self._draw_circle(obj.x - self.MAX_X, obj.y - self.MAX_Y, obj.coll, col_xy_wrap)

        # Draw object lines
        for i in range(0, obj.pts - 2, 2):
            self._draw_line(obj.pt[i].x, obj.pt[i].y, obj.pt[i + 1].x, obj.pt[i + 1].y, colour)
            # Draw copy if wrapping over screen boundary
            if wrap_x_min and (obj.pt[i].x < 0 or obj.pt[i + 1].x < 0):
                self._draw_line(obj.pt[i].x + self.MAX_X, obj.pt[i].y, obj.pt[i + 1].x + self.MAX_X, obj.pt[i + 1].y, colour)
            elif wrap_x_max and (obj.pt[i].x > self.MAX_X or obj.pt[i + 1].x > self.MAX_X):
                self._draw_line(obj.pt[i].x - self.MAX_X, obj.pt[i].y, obj.pt[i + 1].x - self.MAX_X, obj.pt[i + 1].y, colour)
            if wrap_y_min and (obj.pt[i].y < 0 or obj.pt[i + 1].y < 0):
                self._draw_line(obj.pt[i].x, obj.pt[i].y + self.MAX_Y, obj.pt[i + 1].x, obj.pt[i + 1].y + self.MAX_Y, colour)
            elif wrap_y_max and (obj.pt[i].y > self.MAX_Y or obj.pt[i + 1].y > self.MAX_Y):
                self._draw_line(obj.pt[i].x, obj.pt[i].y - self.MAX_Y, obj.pt[i + 1].x, obj.pt[i + 1].y - self.MAX_Y, colour)
            # Consider corner cases also
            if wrap_x_min and wrap_y_min and (obj.pt[i].x < 0 or obj.pt[i + 1].x < 0 or obj.pt[i].y < 0 or obj.pt[i + 1].y < 0):
                self._draw_line(obj.pt[i].x + self.MAX_X, obj.pt[i].y + self.MAX_Y, obj.pt[i + 1].x + self.MAX_X, obj.pt[i + 1].y + self.MAX_Y, colour)
            elif wrap_x_min and wrap_y_max and (obj.pt[i].x < 0 or obj.pt[i + 1].x < 0 or obj.pt[i].y > self.MAX_Y or obj.pt[i + 1].y > self.MAX_Y):
                self._draw_line(obj.pt[i].x + self.MAX_X, obj.pt[i].y - self.MAX_Y, obj.pt[i + 1].x + self.MAX_X, obj.pt[i + 1].y - self.MAX_Y, colour)
            elif wrap_x_max and wrap_y_min and (obj.pt[i].x > self.MAX_X or obj.pt[i + 1].x > self.MAX_X or obj.pt[i].y < 0 or obj.pt[i + 1].y < 0):
                self._draw_line(obj.pt[i].x - self.MAX_X, obj.pt[i].y + self.MAX_Y, obj.pt[i + 1].x - self.MAX_X, obj.pt[i + 1].y + self.MAX_Y, colour)
            elif wrap_x_max and wrap_y_max and (obj.pt[i].x > self.MAX_X or obj.pt[i + 1].x > self.MAX_X or obj.pt[i].y > self.MAX_Y or obj.pt[i + 1].y > self.MAX_Y):
                self._draw_line(obj.pt[i].x - self.MAX_X, obj.pt[i].y - self.MAX_Y, obj.pt[i + 1].x - self.MAX_X, obj.pt[i + 1].y - self.MAX_Y, colour)

   
    def _draw_object(self, obj, explode, hitbox=False):
        """Draw game object."""
        self._draw_object_lines(obj, hitbox, obj.back_colour)
        if (obj.exp > -1 and obj.tumble == 0) or (obj.size > 0 and obj.tumble != 0) or self.score.show:
            self._move_object(obj, explode)
            c = obj.colour
            if self.ship.damage == False and obj.colour == self.display.green:
                c = self.display.red
            if obj.exp > 30:
                c = self.white_shades[60 - obj.exp]
            self._draw_object_lines(obj, hitbox, c)

    def _slow_ship(self):
        """Slow ship down automatically."""
        if self.ship.ax != 0:
            self.ship.ax = self.ship.ax * 199 // 200
        if self.ship.ay != 0:
            self.ship.ay = self.ship.ay * 199 // 200
        '''
        if self.ship.ax < 5 and self.ship.ax > -5:
            self.ship.ax = 0
        if self.ship.ay < 5 and self.ship.ay > -5:
            self.ship.ay = 0
        '''

    def _move_object(self, obj, explode):
        """Move and update object state."""
        if not obj.active:
            return
        if obj.tumble != 0:
            obj.x += obj.ax * self.asteroid_count // 2
            obj.y += obj.ay * self.asteroid_count // 2
        else:
            obj.x += obj.ax
            obj.y += obj.ay
        
        if obj.x > self.MAX_X:
            obj.x = 0
        if obj.x < 0:
            obj.x = self.MAX_X
        if obj.y > self.MAX_Y:
            obj.y = 0
        if obj.y < 0:
            obj.y = self.MAX_Y
        
        obj.deg += obj.tumble
        while obj.deg > 359:
            obj.deg -= 360
        while obj.deg < 0:
            obj.deg += 360
        
        # Recalculate coordinates of all points in the vector for object position, rotation, scale and explode state
        for i in range(0, obj.pts - 2, 2):
            deg1 = int(obj.deg + obj.ptdeg[i // 2]) + (obj.size // 150) * explode
            while deg1 > 359:
                deg1 -= 360
            deg2 = int(obj.deg + obj.ptdeg[1 + i // 2]) - (obj.size // 150) * explode
            while deg2 > 359:
                deg2 -= 360
            if explode:
                obj.size += 10
            obj.pt[i].x = int(obj.ptrad[i // 2] * obj.size * obj.scale * self.icos[deg1] // 10000 + obj.x)
            obj.pt[i].y = int(obj.ptrad[i // 2] * obj.size * obj.scale * self.isin[deg1] // 10000 + obj.y)
            obj.pt[i + 1].x = int(obj.ptrad[1 + i // 2] * obj.size * obj.scale * self.icos[deg2] // 10000 + obj.x)
            obj.pt[i + 1].y = int(obj.ptrad[1 + i // 2] * obj.size * obj.scale * self.isin[deg2] // 10000 + obj.y)
    
    def _thrust(self):
        """Apply thrust to ship."""
        self.ship.ax = self.ship.ax + self.icos[self.ship.deg] // 150
        self.ship.ay = self.ship.ay + self.isin[self.ship.deg] // 150
        self._init_exhaust()
    
    def _init_exhaust(self):
        """Initialize exhaust particles."""
        if self.fps > 20 or (self.fps > 18 and self.active_exhaust < 20) or (self.fps > 16 and self.active_exhaust < 10):  
            i = 0
            for j in range(0, len(self.exhausty), 2):
                if i == len(self.exhausty) - 2:
                    i = 0
                else:
                    i += 2
                if self.exhausty[i].active == False:
                    self.exhausty[i].active = True
                    self.exhausty[i + 1].active = True
                    self.exhausty[i].x = self.ship.pt[2].x
                    self.exhausty[i].y = self.ship.pt[2].y
                    self.exhausty[i + 1].x = self.ship.pt[3].x
                    self.exhausty[i + 1].y = self.ship.pt[3].y
                    if self.ship.deg > 179:
                        deg = self.ship.deg - 180
                    else:
                        deg = self.ship.deg + 180
                    self.exhausty[i].ax = self.ship.ax + self.icos[deg] // 10 * 1 + randint(-10, 10) * 10
                    self.exhausty[i].ay = self.ship.ay + self.isin[deg] // 10 * 1 + randint(-10, 10) * 10
                    self.exhausty[i + 1].ax = self.ship.ax + self.icos[deg] // 10 * 1 + randint(-10, 10) * 10
                    self.exhausty[i + 1].ay = self.ship.ay + self.isin[deg] // 10 * 1 + randint(-10, 10) * 10
                    return
    
    def _show_exhaust(self):
        """Show exhaust particles."""
        active_count = 0
        for i in self.exhausty:
            if i.active == True:
                i.exp += 1
                self._draw_point(i.x, i.y, self.display.black)
                if i.exp > 31:
                    i.active = False
                    i.exp = 0
                else:
                    active_count += 1
                    i.x += i.ax
                    i.y += i.ay
                    c = self.display.black
                    if i.exp < 31:
                        if randint(0, 1):
                            c = self.red_shades[31 - i.exp]
                        else:
                            c = self.yellow_shades[31 - i.exp]
                    if randint(0, 1):
                        c = self.red_shades[31]
                    else:
                        c = self.yellow_shades[31]
                    self._draw_point(i.x, i.y, c)
        return active_count
    
    def _buttons(self, fps):
        """ Handle button input. """
        if self.ship.exp == 0:
            # Only allow control when ship is not exploding
            if self.display.is_key_held(self.KEY_UP):
                self.ship.deg += 2 + (50 - fps) // 5
                if self.ship.deg > 359:
                    self.ship.deg = 0
            if self.display.is_key_held(self.KEY_DOWN):
                self.ship.deg -= 2 + (50 - fps) // 5
                if self.ship.deg < 0:
                    self.ship.deg = 359
            if self.display.is_key_held(self.KEY_RUN):
                self._thrust()
            if (self.display.is_key_held(self.KEY_FIRE) and self.ship.damage) or self.demo:
                if self.rfire > (25 * fps) // 100:
                    self.rfire = 0
                    self._fire()
            if self.demo:
                self.ship.deg += 1
                if self.ship.deg > 359:
                    self.ship.deg = 0
        if self.display.is_key_held(self.KEY_LEFT) and self.display.is_key_held(self.KEY_START):
            self.display.reset()
        elif self.display.is_key_held(self.KEY_RIGHT) and self.display.is_key_held(self.KEY_START):
            self.display.fill(self.display.blue)
    
    def _fire(self):
        """Fire a missile."""
        for i in self.bullets:
            if i.active == False:
                i.active = True
                i.x = self.ship.pt[0].x
                i.y = self.ship.pt[0].y
                i.ax = self.ship.ax + self.icos[self.ship.deg] // 10 * 3
                i.ay = self.ship.ay + self.isin[self.ship.deg] // 10 * 3
                return
    
    def _spawn_asteroid(self, objs, last):
        """Spawn a new asteroid from an existing one."""
        i = last
        for j in range(len(objs)):
            if i == len(objs) - 1:
                i = 0
            else:
                i += 1
            if objs[i].active == False:
                objs[i].active = True
                objs[i].x = objs[last].x + randint(-2000, 2000) * 5
                objs[i].y = objs[last].y + randint(-2000, 2000) * 5
                objs[i].ax = randint(-40, 40) * 20
                objs[i].ay = randint(-40, 40) * 20
                if objs[i].ax < 1000:
                    objs[i].ax += 200
                if objs[i].ay < 1000:
                    objs[i].ay += 200
                objs[i].size = objs[last].size
                objs[i].calc_coll(self.hitbox_scale)
                objs[i].exp = 0
                return
    
    def _move_miss_new(self):
        """Move missiles and check collisions."""
        for i in range(0, self.max_missiles):
            if (self.bullets[i].active and self.bullets[i].x > -self.SCALE and self.bullets[i].x < self.MAX_X + self.SCALE \
                and self.bullets[i].y > -self.SCALE and self.bullets[i].y < self.MAX_Y + self.SCALE
            ):
                # Active bullet is within screen playing area.
                # Erase it
                self._draw_point(self.bullets[i].x, self.bullets[i].y, self.display.black)
                # Move it
                self.bullets[i].x = self.bullets[i].x + self.bullets[i].ax
                self.bullets[i].y = self.bullets[i].y + self.bullets[i].ay
                # Draw it randomly in red or white
                if randint(0, 1):
                    c = self.red_shades[31]
                else:
                    c = self.display.white
                self._draw_point(self.bullets[i].x, self.bullets[i].y, c)
                # Check asteroids for collision with bullet
                for j in range(0, len(self.asteroid)):
                    if (self.asteroid[j].active and self.bullets[i].active and
                        self.bullets[i].x < self.asteroid[j].x + self.asteroid[j].coll and 
                        self.bullets[i].x > self.asteroid[j].x - self.asteroid[j].coll and 
                        self.bullets[i].y < self.asteroid[j].y + self.asteroid[j].coll and 
                        self.bullets[i].y > self.asteroid[j].y - self.asteroid[j].coll and 
                        self.asteroid[j].size > 0 and 
                        self.asteroid[j].exp == 0 and 
                        self.ship.damage
                    ):
                        # Asteroid missile collision
                        self.display.pixel(int(self.bullets[i].x // self.SCALE), int(self.bullets[i].y // self.SCALE), self.display.black)
                        self.score.value += scoring[self.asteroid[j].size // self.SCALE]
                        self.asteroid[j].size -= self.SCALE
                        if self.asteroid[j].size > 100:
                            self._spawn_asteroid(self.asteroid, j)
                            self._spawn_asteroid(self.asteroid, j)
                        self.asteroid[j].exp = 1
                        self.asteroid[j].tumble = 0
                        self.asteroid[j].ax = 0
                        self.asteroid[j].ay = 0
                        if self.hitbox_debug:
                            # Erase hitbox as asteroid is destroyed
                            self._draw_circle(self.asteroid[j].x, self.asteroid[j].y, self.asteroid[j].coll, self.asteroid[j].back_colour)
                        self.bullets[i].active = False
            else:
                self.bullets[i].active = False
    
    def _move_asteroid(self):
        """Move asteroids and check collisions with ship."""
        self.asteroid_count = 0
        for i in range(0, len(self.asteroid)):
            self.asteroid_count += (self.asteroid[i].active == True)
            if self.asteroid[i].active:
                if self.asteroid[i].exp > 0:
                    self.asteroid[i].exp += 1
                self._draw_object(self.asteroid[i], (self.asteroid[i].exp > 0), self.hitbox_debug)
                if (self.ship.damage and self.ship.exp == 0 and 
                    self.ship.x < self.asteroid[i].x + self.asteroid[i].coll and 
                    self.ship.x > self.asteroid[i].x - self.asteroid[i].coll and 
                    self.ship.y < self.asteroid[i].y + self.asteroid[i].coll and 
                    self.ship.y > self.asteroid[i].y - self.asteroid[i].coll and 
                    self.asteroid[i].exp == 0):
                    # Start ship explosion
                    self.ship.exp = 1
                if self.asteroid[i].size < 1 or self.asteroid[i].exp > 59:
                    self._draw_object(self.asteroid[i], True)
                    self.asteroid[i].active = False
                    self.asteroid[i].exp = 0
    
    def _animate_star_zoom(self, y):
        """Add a star to the field."""
        for i in self.expPnts:
            if i.active == False:
                i.active = True
                i.x = self.MAX_X // 2
                i.y = y
                i.ax = randint(-self.SCALE, self.SCALE) * 10 // 1
                i.ay = randint(-self.SCALE, self.SCALE) * 10 // 1
                break

        self._explode()
    
    def _init_stars(self):
        """Reset velocity of all stars"""
        for i in self.expPnts:
            i.active = False
            i.ax = 0
            i.ay = 0

    def _stars(self):
        """Update and show star field."""
        j = 0
        k = 0
        for i in range(0, self.MAXSCREEN_X // 26):
            if self.expPnts[i].active:
                if self.expPnts[i].x >= 0 and self.expPnts[i].x <= self.MAX_X and self.expPnts[i].y >= 0 and self.expPnts[i].y <= self.MAX_Y:
                    self._draw_point(self.expPnts[i].x, self.expPnts[i].y, self.display.black)
                    if self.ship.deg > 179:
                        deg = self.ship.deg - 180
                    else:
                        deg = self.ship.deg + 180
                    self.expPnts[i].x = int(self.expPnts[i].x - self.ship.ax + self.icos[deg] // 10)
                    self.expPnts[i].y = int(self.expPnts[i].y - self.ship.ay + self.isin[deg] // 10)
                    colour = self.display.white
                    self._draw_point(self.expPnts[i].x, self.expPnts[i].y, colour)
                    j += 1
                else:
                    self._draw_point(self.expPnts[i].x, self.expPnts[i].y, self.display.black)
                    self.expPnts[i].active = False
            else:
                k = i
        
        if j < self.MAXSCREEN_X // 26 - 1:
            if self.expPnts[k].x < 0:
                self.expPnts[k].x = self.MAX_X
                self.expPnts[k].y = randint(0, self.MAX_Y)
            elif self.expPnts[k].x > self.MAX_X:
                self.expPnts[k].x = 0
                self.expPnts[k].y = randint(0, self.MAX_Y)
            elif self.expPnts[k].y < 0:
                self.expPnts[k].y = self.MAX_Y
                self.expPnts[k].x = randint(0, self.MAX_X)
            elif self.expPnts[k].y > self.MAX_Y:
                self.expPnts[k].y = 0
                self.expPnts[k].x = randint(0, self.MAX_X)
            else:
                self.expPnts[k].x = randint(0, self.MAX_X)
                self.expPnts[k].y = randint(0, self.MAX_Y)
            self.expPnts[k].active = True
    
    def _init_explode(self, objhit, n, s):
        """Initialize explosion particles."""
        for i in range(0, n):
            self._draw_point(self.expPnts[i].x, self.expPnts[i].y, self.display.black)
            self.expPnts[i].active = True
            self.expPnts[i].x = objhit.x
            self.expPnts[i].y = objhit.y
            self.expPnts[i].ax = objhit.ax + randint(-self.SCALE, self.SCALE) * 10 // s
            self.expPnts[i].ay = objhit.ay + randint(-self.SCALE, self.SCALE) * 10 // s
    
    def _explode(self):
        """Update and show explosion."""
        for i in range(0, len(self.expPnts)):
            if self.expPnts[i].active:
                if self.expPnts[i].x > -self.SCALE and self.expPnts[i].x < self.MAX_X + self.SCALE \
                    and self.expPnts[i].y > -self.SCALE and self.expPnts[i].y < self.MAX_Y + self.SCALE and self.expPnts[i].exp < 51:
                    self._draw_point(self.expPnts[i].x, self.expPnts[i].y, self.display.black)
                    self.expPnts[i].x = int(self.expPnts[i].x + self.expPnts[i].ax)
                    self.expPnts[i].y = int(self.expPnts[i].y + self.expPnts[i].ay)
                    colour = self.display.white
                    if self.expPnts[i].exp > 20:
                        colour = self.white_shades[51 - self.expPnts[i].exp]
                    self._draw_point(self.expPnts[i].x, self.expPnts[i].y, colour)
                    self.expPnts[i].exp += 1
                else:
                    self._draw_point(self.expPnts[i].x, self.expPnts[i].y, self.display.black)
                    self.expPnts[i].active = False
                    self.expPnts[i].exp = 0
    
    def _explode_cleanup(self):
        """Clean up explosion particles."""
        for i in range(0, len(self.expPnts)):
            if self.expPnts[i].active or 0:
                self._draw_point(self.expPnts[i].x, self.expPnts[i].y, self.display.black)
                self.expPnts[i].active = False
                self.expPnts[i].exp = 0
    
    def _ship_condition(self):
        """Check and update ship state."""
        if self.ship.exp >= 60:
            # Ship finished exploding
            self.score.lives -= 1
            # Wipe lives indicators so they redraw showing only remaining lives count
            self.display.fill_rect((self.MAX_X - self.SCALE * 90)//self.SCALE, 0, 80, 38, self.display.black)
            if self.score.lives == 0:
                self._game_over()
            else:
                self._new_ship()
        elif self.ship.exp > 0:
            self.ship.exp += 1
    
    def _no_damage(self, timer):
        """Callback: enable ship damage."""
        self.ship.damage = True
    
    def initialize(self):
        """Initialize the game. Call this after construction."""
        self.display.fill(self.display.black)
        self._init_title_letts()
        self._init_isin()
        self._init_icos()
        self._init_explosion()
        self._init_big_score()
        self._init_game_over()
        self._init_asteroids()
        self._init_missiles()
    
    def _calc_fps(self):
        """ Calculate frames per second """
        fps = 1_000_000 // self.display.ticks_diff(self.display.ticks_us(), self.gticks)
        self.gticks = self.display.ticks_us()
        # Display fps on screen for debugging
        #self.display.fill_rect(10, self.MAXSCREEN_Y - 28, 42, 26, self.display.black)
        #self.display.text(f"{fps}", 12, self.MAXSCREEN_Y - 25, self.display.blue)

        return fps

    def update(self):
        """Update and render the game. Call this every frame."""
        fps = 0
        if self.game_mode == GAME_MODE.PLAY:
            self._show_small_score(self.display.green) # Update score first as it blanks area behind digits
            if not self.score.show:
                self._move_asteroid() # This resets asteroid_count to number active as it changes during game
            if self.asteroid_count == 0:
                # Reset level and add more asteroids
                #self.score.show = True # Stops object movement
                self.num_asteroids += self.asteroid_inc
                self._reset_asteroids()
                #self._show_big_score()
                self.ship.damage = False
                self.timer.init(mode=self.timer.ONE_SHOT, period=2000, callback=self._no_damage)
            
            self._slow_ship()
            self._ship_condition()   # Animates ship explosion and ends life and resets if fully exploded
            self._draw_object(self.ship, self.ship.exp > 0)
            self._move_miss_new()
            self.active_exhaust = self._show_exhaust()
            self._stars()
            self._draw_lives_remaining()
            self._explode() # Update explosion particles (which are also the stars)
            self.rfire += 1 # Increment frames since last fired counter
            fps = self._calc_fps()
            self._buttons(fps)
        else:
            fps = self._calc_fps()
            if self.game_mode == GAME_MODE.TITLE:
                self._show_title(self.titleLetts)
            elif self.game_mode == GAME_MODE.GAME_OVER:
                self._show_title(self.over_list)

        self.fps = fps
        self.display.show() # Trigger display update on hardware which does not immediately render drawing commands

        return fps
