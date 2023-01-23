import pygame
from game_data import tile_size, scaling_factor, controls
from random import randint
from math import sin
from visual_FX import Radial_Blast
from lighting import Light
from support import pos_for_center

# SET UP FOR PLATFORMER SINCE PLATFORMERS ARE HARDER TO CREATE A PLAYER FOR
class Player(pygame.sprite.Sprite):
    def __init__(self, spawn, surface):
        super().__init__()
        self.surface = surface

        # -- player setup --
        self.start_radius = 20
        self.rect = pygame.Rect(spawn[0], spawn[1], self.start_radius, self.start_radius)

        # circle = (radius, (posx, posy)) <- pos is top left NOT center
        self.circles = [[self.start_radius, [self.rect.centerx, self.rect.centery]]]
        self.smallest_circle = 6
        self.largest_circle = 500
        self.subtract_r = 40  # (x100)

        # radial effects
        self.click_effects = pygame.sprite.Group()
        self.blast_radius = 15
        self.blast_colour = 'white'
        self.blast_width = 123
        self.blast_speed = 533
        self.blast_duration = 214

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
        self.flame_amplitude = 10  # flame tail x force constant
        self.flame_speed = 200  # speed of flame sine wave  (x1000)
        self.flame_volume = 20  # amount of x randomness per particle
        self.flame_timer = 0
        self.apply_flame = False
        self.flame_pressed = False

        # - Click Bursts -
        self.mouse_clicked = False  # whether mouse has been clicked or not
        self.allow_hold_click = False  # allow holding of the click effect
        self.allow_hold_pressed = False  # whether the button to toggle allow hold click is pressed or not

# -- checks --

    def get_input(self, dt, mouse_pos, tiles):
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
            self.mouse_clicked = True
        elif not pygame.mouse.get_pressed()[0]:
            self.mouse_clicked = False

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



    # - respawn -

    def invoke_respawn(self):
        self.respawn = True

    def get_respawn(self):
        return self.respawn

    def player_respawn(self, spawn):
        self.rect.x, self.rect.y = spawn.x, spawn.y  # set position to respawn point
        self.sync_hitbox()
        if spawn.player_facing == 'right':
            self.facing_right = 1
        else:
            self.facing_right = -1
        self.direction = pygame.math.Vector2(0, 0)  # reset movement
        self.dashing = False  # end any dashes on respawn
        self.dash_timer = self.dash_max  # prevent dash immediately on reset
        self.crouching = False  # end any crouching on respawn
        self.jumping = False  # end any jumps on respawn
        self.respawn = False

# -- update methods --

    # checks collision for a given hitbox against given tiles on the x
    def collision_x(self, hitbox, tiles):
        collision_offset = [0, 0]  # position hitbox is to be corrected to after checks
        self.on_wall = False

        top = False
        top_margin = False
        bottom = False
        bottom_margin = False

        for tile in tiles:
            if tile.hitbox.colliderect(hitbox):
                # - normal collision checks -
                # abs ensures only the desired side registers collision
                # not having collisions dependant on status allows hitboxes to change size
                if abs(tile.hitbox.right - hitbox.left) < self.collision_tolerance:
                    collision_offset[0] = tile.hitbox.right - hitbox.left
                    self.on_wall_right = False  # which side is player clinging?
                elif abs(tile.hitbox.left - hitbox.right) < self.collision_tolerance:
                    collision_offset[0] = tile.hitbox.left - hitbox.right
                    self.on_wall_right = True  # which side is player clinging?

                #- horizontal corner correction - (for both side collisions)

                # checking allowed to corner correct
                # Use a diagram. Please
                # checks if the relevant horizontal raycasts on the player hitbox are within a tile or not
                # this allows determination as to whether on the end of a column of tiles or not

                # top
                if tile.hitbox.top <= hitbox.top <= tile.hitbox.bottom:
                    top = True
                if tile.hitbox.top <= hitbox.top + self.corner_correction <= tile.hitbox.bottom:
                    top_margin = True
                # stores tile for later potential corner correction
                if hitbox.top < tile.hitbox.bottom < hitbox.top + self.corner_correction:
                    collision_offset[1] = tile.hitbox.bottom - hitbox.top

                # bottom
                if tile.hitbox.top <= hitbox.bottom <= tile.hitbox.bottom:
                    bottom = True
                if tile.hitbox.top <= hitbox.bottom - self.corner_correction <= tile.hitbox.bottom:
                    bottom_margin = True
                if hitbox.bottom > tile.hitbox.top > hitbox.bottom - self.corner_correction:
                    collision_offset[1] = -(hitbox.bottom - tile.hitbox.top)

        # -- application of offsets --
        # must occur after checks so that corner correction can check every contacted tile
        # without movement of hitbox half way through checks
        # - collision correction -
        hitbox.x += collision_offset[0]
        # - corner correction -
        # adding velocity requirement prevents correction when just walking towards a wall. Only works at a higher
        # velocity like during a dash or if the player is boosted.
        if ((top and not top_margin) or (bottom and not bottom_margin)) and abs(self.direction.x) >= self.dash_speed:
            hitbox.y += collision_offset[1]

        self.sync_rect()

    # checks collision for a given hitbox against given tiles on the y
    def collision_y(self, hitbox, tiles):
        collision_offset = [0, 0]

        left = False
        left_margin = False
        right = False
        right_margin = False

        bonk = False

        for tile in tiles:
            if tile.hitbox.colliderect(hitbox):
                # abs ensures only the desired side registers collision
                if abs(tile.hitbox.top - hitbox.bottom) < self.collision_tolerance:
                    collision_offset[1] = tile.hitbox.top - hitbox.bottom
                # collision with bottom of tile
                elif abs(tile.hitbox.bottom - hitbox.top) < self.collision_tolerance:
                    collision_offset[1] = tile.hitbox.bottom - hitbox.top

                    # - vertical corner correction - (only for top, not bottom collision)
                    # left
                    if tile.hitbox.left <= hitbox.left <= tile.hitbox.right:
                        left = True
                    if tile.hitbox.left <= hitbox.left + self.corner_correction <= tile.hitbox.right:
                        left_margin = True
                    if hitbox.left < tile.hitbox.right < hitbox.left + self.corner_correction:
                        collision_offset[0] = tile.hitbox.right - hitbox.left

                    # right
                    if tile.hitbox.left <= hitbox.right <= tile.hitbox.right:
                        right = True
                    if tile.hitbox.left <= hitbox.right - self.corner_correction <= tile.hitbox.right:
                        right_margin = True
                    if hitbox.right > tile.hitbox.left > hitbox.right - self.corner_correction:
                        collision_offset[0] = -(hitbox.right - tile.hitbox.left)

                    bonk = True

        # -- application of offsets --
        # - normal collisions -
        hitbox.y += collision_offset[1]
        # - corner correction -
        if (left and not left_margin) or (right and not right_margin):
            hitbox.x += collision_offset[0]
        # drop by zeroing upwards velocity if corner correction isn't necessary and hit bottom of tile
        elif bonk:
            self.direction.y = 0

        # resyncs up rect to the hitbox
        self.sync_rect()

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

        # - collision and movement -
        # applies direction to player then resyncs hitbox (included in most movement/collision functions)
        # HITBOX MUST BE SYNCED AFTER EVERY MOVE OF PLAYER RECT
        # x and y collisions are separated to make diagonal collisions easier and simpler to handle
        self.collision_x(self.hitbox, tiles)
        self.collision_y(self.hitbox, tiles)

# -- visual methods --

    def draw(self):
        for blast in self.click_effects:
            blast.draw()

        for circle in self.circles:
            pygame.draw.circle(self.surface, 'red', circle[1], circle[0])

