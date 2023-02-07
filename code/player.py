import pygame
from game_data import tile_size, scaling_factor, controls
from random import randint
from math import sin
from visual_FX import Radial_Blast
from support import pos_for_center

# SET UP FOR PLATFORMER SINCE PLATFORMERS ARE HARDER TO CREATE A PLAYER FOR
class Player(pygame.sprite.Sprite):
    def __init__(self, spawn, surface):
        super().__init__()
        self.surface = surface

        # -- player setup --
        self.start_radius = 20
        self.rect = pygame.Rect(spawn[0], spawn[1], self.start_radius, self.start_radius)
        self.default_vals = {"subtract r": 40, "blast width": 123, "blast speed": 533,
                             "blast duration": 214, "screen shake max": 88, "max screen shake": 60,
                             "flame amplitude": 10, "flame speed": 200, "flame volume": 20}

        # circle = (radius, (posx, posy)) <- pos is top left NOT center
        self.circles = [[self.start_radius, [self.rect.centerx, self.rect.centery]]]
        self.smallest_circle = 6
        self.largest_circle = 500
        self.subtract_r = self.default_vals["subtract r"]  # (x100)

        # radial effects
        self.click_effects = pygame.sprite.Group()
        self.blast_radius = 15
        self.blast_colour = 'white'
        self.blast_width = self.default_vals["blast width"]
        self.blast_speed = self.default_vals["blast speed"]
        self.blast_duration = self.default_vals["blast duration"]

        # screen shake
        self.apply_screen_shake = True
        self.shake_pressed = False
        self.screen_shake_max = self.default_vals["screen shake max"]
        self.screen_shake_timer = 0
        self.screen_shake = [0, 0]
        self.max_screen_shake = self.default_vals["max screen shake"]

        # - hitbox -
        self.hitbox = pygame.Rect(spawn[0], spawn[1], self.start_radius, self.start_radius)

        self.respawn = False

        # -- player movement --
        self.direction = pygame.math.Vector2(0, 0)  # allows cleaner movement by storing both x and y direction
        # collisions -- provides a buffer allowing late collision
        self.collision_tolerance = tile_size
        self.corner_correction = 8  # tolerance for correcting player on edges of tiles (essentially rounded corners)

        # - Tail Bloom - (Tail particles expand rather than contract)
        self.tail_bloom = 1  # 1 == off, -1 == on
        self.bloom_pressed = False

        # - Tail Gravity -
        self.gravity = 2
        self.apply_gravity = False
        self.gravity_pressed = False

        # - Tail Flame -
        self.flamey = 3  # flame tail size (constant upward force)
        self.flame_amplitude = self.default_vals["flame amplitude"]  # flame tail x force constant
        self.flame_speed = self.default_vals["flame speed"]  # speed of flame sine wave  (x1000)
        self.flame_volume = self.default_vals["flame volume"]  # amount of x randomness per particle
        self.flame_timer = 0
        self.apply_flame = False
        self.flame_pressed = False

        # - Click Bursts -
        self.mouse_clicked = False  # whether mouse has been clicked or not
        self.allow_hold_click = False  # allow holding of the click effect
        self.allow_hold_pressed = False  # whether the button to toggle allow hold click is pressed or not

# -- checks --

    def get_input(self, dt, mouse_pos, tiles):
        self.screen_shake = [0, 0]
        self.direction.x = 0
        keys = pygame.key.get_pressed()

        # --- TAIL CONTROLS ---

        # tail size
        key = controls["+/- Tail Length/Bloom Speed"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.subtract_r += 1 * dt
        elif keys[key]:
            self.subtract_r -= 1 * dt
        if self.subtract_r < 0:
            self.subtract_r = 0

        # --- FLAME CONTROLS ---

        # flame rate
        key = controls["+/- Flame Rate"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.flame_speed -= 5 * dt
        elif keys[key]:
            self.flame_speed += 5 * dt
        if self.flame_speed < 0:
            self.flame_speed = 0

        # flame volume
        key = controls["+/- Flame Volume"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.flame_volume -= 2 * dt
        elif keys[key]:
            self.flame_volume += 2 * dt
        if self.flame_volume < 0:
            self.flame_volume = 0

        # flame amplitude
        key = controls["+/- Flame Amplitude"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.flame_amplitude -= 2 * dt
        elif keys[key]:
            self.flame_amplitude += 2 * dt
        if self.flame_amplitude < 0:
            self.flame_amplitude = 0

        # --- BLAST CONTROLS ---

        # blasts
        if pygame.mouse.get_pressed()[0] and (not self.mouse_clicked or self.allow_hold_click):
            self.click_effects.add(
                Radial_Blast(self.blast_radius, self.blast_colour, (self.blast_width / 10), self.surface, mouse_pos,
                             (self.blast_speed / 100), self.blast_duration))
            # screen shake
            # reset timer to active
            self.screen_shake_timer = 1

            self.mouse_clicked = True
        elif not pygame.mouse.get_pressed()[0]:
            self.mouse_clicked = False
            # if not click and timer greater than max, reset to inactive
            if self.screen_shake_timer > self.screen_shake_max:
                self.screen_shake_timer = 0

        # blast width
        key = controls["+/- Blast Width"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.blast_width -= 2 * dt
        elif keys[key]:
            self.blast_width += 2 * dt
        if self.blast_width < 1:
            self.blast_width = 1

        # blast speed
        key = controls["+/- Blast Speed"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.blast_speed -= 2 * dt
        elif keys[key]:
            self.blast_speed += 2 * dt
        if self.blast_speed < 0:
            self.blast_speed = 0

        # blast duration
        key = controls["+/- Blast Duration"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.blast_duration -= 0.5 * dt
        elif keys[key]:
            self.blast_duration += 0.5 * dt
        if self.blast_duration < 0:
            self.blast_duration = 0

        # --- SCREEN SHAKE CONTROLS ---
        key = controls["+/- Shake Duration"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.screen_shake_max -= 2 * dt
        elif keys[key]:
            self.screen_shake_max += 2 * dt
        if self.screen_shake_max < 0:
            self.screen_shake_max = 0

        key = controls["+/- Shake Intensity"]
        if keys[key] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.max_screen_shake -= 2 * dt
        elif keys[key]:
            self.max_screen_shake += 2 * dt
        if self.max_screen_shake < 0:
            self.max_screen_shake = 0

        # --- TOGGLES ---

        # tail bloom
        key = controls["Toggle Tail Bloom"]
        if keys[key] and not self.bloom_pressed:
            self.tail_bloom = -self.tail_bloom
            self.bloom_pressed = True
        elif not keys[key]:
            self.bloom_pressed = False

        # gravity
        key = controls["Toggle Gravity"]
        if keys[key] and not self.gravity_pressed:
            self.apply_gravity = not self.apply_gravity
            self.apply_flame = False
            self.gravity_pressed = True
        elif not keys[key]:
            self.gravity_pressed = False

        # flame
        key = controls["Toggle Flame"]
        if keys[key] and not self.flame_pressed:
            self.apply_flame = not self.apply_flame
            self.apply_gravity = False
            self.flame_pressed = True
        elif not keys[key]:
            self.flame_pressed = False

        # allow hold click
        key = controls["Toggle Repeat Blast"]
        if keys[key] and not self.allow_hold_pressed:
            self.allow_hold_click = not self.allow_hold_click
            self.allow_hold_pressed = True
        elif not keys[key]:
            self.allow_hold_pressed = False

        # toggle screen shake
        key = controls["Toggle Screen Shake"]
        if keys[key] and not self.shake_pressed:
            self.apply_screen_shake = not self.apply_screen_shake
            self.shake_pressed = True
            self.screen_shake_timer = 0
        elif not keys[key]:
            self.shake_pressed = False

    # - respawn -

    def player_reset(self):
        self.tail_bloom = 1
        self.subtract_r = self.default_vals["subtract r"]
        self.blast_width = self.default_vals["blast width"]
        self.blast_speed = self.default_vals["blast speed"]
        self.blast_duration = self.default_vals["blast duration"]
        self.screen_shake_max = self.default_vals["screen shake max"]
        self.max_screen_shake = self.default_vals["max screen shake"]
        self.flame_amplitude = self.default_vals["flame amplitude"]
        self.flame_speed = self.default_vals["flame speed"]
        self.flame_volume = self.default_vals["flame volume"]

# -- update methods --

    def apply_x_direction(self, dt):
        x_move = round(self.direction.x * dt)

        self.rect.x += x_move
        self.sync_hitbox()

        for circle in self.circles:
            circle[1][0] += x_move

    # application of y direction
    def apply_gravity_vel(self, dt):
        for circle in range(len(self.circles) - 1):  # - 1 to disclude head circle
            self.circles[circle][1][1] += round(self.gravity * dt)

    # All the random division rubbish is my way of making all the units whole numbers for the settings menu
    # then converting back into the decimal "equivalents" for real use. Super janky but it works
    def apply_flame_vel(self, dt):
        for circle in range(len(self.circles) - 1):
            self.circles[circle][1][1] -= round(self.flamey * dt)

            random_x_shift = randint(-int(self.flame_volume / 10), int(self.flame_volume / 10))
            x_modifier = (self.flame_amplitude / 10) * sin(self.flame_timer * (self.flame_speed / 1000)) + random_x_shift
            self.circles[circle][1][0] += round(x_modifier * dt)

        self.flame_timer += 1  # only increases when flame is active (only neccessary when active)

    # syncs the player's current and stored hitboxes with the player rect for proper collisions. For use after movement of player rect.
    def sync_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    # syncs the player's rect with the current hitbox for proper movement. For use after movement of main hitbox
    def sync_rect(self):
        self.rect.midbottom = self.hitbox.midbottom

    def get_screen_shake(self):
        return self.screen_shake

    def update(self, mouse_pos, dt, tiles):
        self.sync_hitbox()  # just in case

        # -- INPUT --
        self.get_input(dt, mouse_pos, tiles)
        self.rect.centerx = mouse_pos[0]
        self.rect.centery = mouse_pos[1]

        r_circles = []
        for circle in range(len(self.circles)):
            # subtract from each circle's radius * bloom (either -1 or 1, makes go in or out)
            self.circles[circle][0] -= self.tail_bloom * (self.subtract_r / 100) * dt
            # remove circles if too big or too small
            if self.largest_circle < self.circles[circle][0] or self.circles[circle][0] < self.smallest_circle:
                r_circles.append(self.circles[circle])
        for circle in r_circles:
            self.circles.remove(circle)
        self.circles.append([self.start_radius, [self.rect.centerx, self.rect.centery]])

        # apply directional modifiers based on state
        if self.apply_gravity:
            self.apply_gravity_vel(dt)
        elif self.apply_flame:
            self.apply_flame_vel(dt)

        # -- CHECKS/UPDATE --
        for blast in self.click_effects:
            blast.update()

        # if timer active and less than max, generate shake
        if 0 < self.screen_shake_timer <= (self.screen_shake_max / 10) and self.apply_screen_shake:
            self.screen_shake[0] = randint(-int(self.max_screen_shake / 10), int(self.max_screen_shake / 10))
            self.screen_shake[1] = randint(-int(self.max_screen_shake / 10), int(self.max_screen_shake / 10))
            self.screen_shake_timer += 1

# -- visual methods --

    def draw(self):
        for blast in self.click_effects:
            blast.draw()

        for circle in self.circles:
            pygame.draw.circle(self.surface, 'red', circle[1], circle[0])

