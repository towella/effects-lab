import pygame
from game_data import tile_size, controller_map, scaling_factor
from lighting import Light
from support import pos_for_center

# SET UP FOR PLATFORMER SINCE PLATFORMERS ARE HARDER TO CREATE A PLAYER FOR
class Player(pygame.sprite.Sprite):
    def __init__(self, spawn, surface, controllers):
        super().__init__()
        self.surface = surface
        self.controllers = controllers

        # -- player setup --
        self.start_radius = 20
        self.rect = pygame.Rect(spawn[0], spawn[1], self.start_radius, self.start_radius)

        # circle = (radius, (posx, posy)) <- pos is top left NOT center
        self.circles = [[self.start_radius, [self.rect.centerx, self.rect.centery]]]
        self.smallest_circle = 6

        self.lights = [Light(self.surface, self.rect.center, (10, 10, 10), False, 30, 20, 0.02)]

        # - hitbox -
        self.hitbox = pygame.Rect(spawn[0], spawn[1], self.start_radius, self.start_radius)

        self.respawn = False

        # -- player movement --
        self.direction = pygame.math.Vector2(0, 0)  # allows cleaner movement by storing both x and y direction
        # collisions -- provides a buffer allowing late collision
        self.collision_tolerance = tile_size
        self.corner_correction = 8  # tolerance for correcting player on edges of tiles (essentially rounded corners)

        # - walk -
        self.speed_x = 2.5
        self.right_pressed = False
        self.left_pressed = False

        # - dash -
        self.dashing = False  # NOT REDUNDANT. IS NECCESSARY. Allows resetting timer while dashing. Also more readable code
        self.dash_speed = 4
        self.dash_pressed = False  # if the dash key is being pressed
        self.dash_max = 12  # max time of dash in frames
        self.dash_timer = self.dash_max  # maxed out to prevent being able to dash on start. Only reset on ground
        self.dash_dir_right = True  # stores the dir for a dash. Prevents changing dir during dash. Only dash cancels
        # - buffer dash -
        self.buffer_dash = False  # is a buffer dash cued up
        self.dashbuff_max = 5  # max time a buffered dash can be cued before it is removed (in frames)
        self.dashbuff_timer = self.dashbuff_max  # times a buffered dash from input (starts on max to prevent jump being cued on start)

# -- checks --

    def get_input(self, dt, tiles):
        self.direction.x = 0
        keys = pygame.key.get_pressed()

        # -- dash --
        # if wanting to dash and not holding the button
        '''if (keys[pygame.K_PERIOD] or self.get_controller_input('dash')) and not self.dash_pressed:
            # if only just started dashing, dashing is true and dash direction is set. Prevents changing dash dir during dash
            if not self.dashing:
                self.dashing = True
                self.dash_dir_right = self.facing_right
            self.dashbuff_timer = 0  # set to 0 ready for next buffdash
            self.dash_pressed = True
        # neccessary to prevent repeated dashes on button hold
        elif not keys[pygame.K_PERIOD] and not self.get_controller_input('dash'):
            self.dash_pressed = False

        self.dash(dt)'''

        # TODO testing, remove
        if keys[pygame.K_r] or self.get_controller_input('dev'):
            self.invoke_respawn()

    # checks controller inputs and returns true or false based on passed check
    # pygame controller docs: https://www.pygame.org/docs/ref/joystick.html
    def get_controller_input(self, input_check):
        # self.controller.get_hat(0) returns tuple (x, y) for d-pad where 0, 0 is centered, -1 = left or down, 1 = right or up
        # the 0 refers to the dpad on the controller

        # check if controllers are connected before getting controller input (done every frame preventing error if suddenly disconnected)
        if len(self.controllers) > 0:
            controller = self.controllers[0]
            if input_check == 'jump' and controller.get_button(controller_map['X']):
                return True
            elif input_check == 'right':
                if controller.get_hat(0)[0] == 1 or (0.2 < controller.get_axis(controller_map['left_analog_x']) <= 1):
                    return True
            elif input_check == 'left':
                if controller.get_hat(0)[0] == -1 or (-0.2 > controller.get_axis(controller_map['left_analog_x']) >= -1):
                    return True
                '''elif input_check == 'up':
                    if controller.get_hat(0)[1] == 1 or (-0.2 > controller.get_axis(controller_map['left_analog_y']) >= -1):
                        return True
                elif input_check == 'down':
                    if controller.get_hat(0)[1] == -1 or (0.2 < controller.get_axis(controller_map['left_analog_y']) <= 1):
                        return True'''
            elif input_check == 'dash' and controller.get_button(controller_map['R2']) > 0.8:
                return True
            elif input_check == 'glide' and (controller.get_button(controller_map['L1']) or controller.get_hat(0)[1] == -1):
                return True
            elif input_check == 'crouch' and (controller.get_hat(0)[1] == -1 or 0.2 < controller.get_axis(controller_map['left_analog_y']) <= 1):  # TODO crouch controls
                return True
            # TODO testing, remove
            elif input_check == 'dev' and controller.get_button(controller_map['right_analog_press']):
                return True
        return False

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

# -- movement methods --

    def dash(self, dt):
        # - reset -
        # reset dash, on ground OR if on the wall and dash completed (not dashing) - allows dash to finish before clinging
        # reset despite button pressed or not (not dependant on button, can only dash with button not pressed)
        if self.on_ground or (self.on_wall and not self.dashing):
            self.dash_timer = 0
        # - setup buffer dash - (only when not crouching)
        # self.dashing is set to false when buffdash is cued. Sets to true on ground so that it can start a normal dash,
        # which resets buffer dashing variables ready for next one
        if self.on_ground and self.dashbuff_timer < self.dashbuff_max and not self.crouching:
            self.dashing = True
        # - start normal dash or continue dash - (only when not crouching)
        # (if dashing and dash duration not exceeded OR buffered dash) AND not crouching, allow dash
        if self.dashing and self.dash_timer < self.dash_max and not self.crouching:
            # - norm dash -
            # add velocity based on facing direction determined at start of dash
            # self.dash_dir_right multiplies by 1 or -1 to change direction of dash speed distance
            self.direction.x += self.dash_speed * self.dash_dir_right
            # dash timer increment
            self.dash_timer += round(1 * dt)

            # - buffer -
            # reset buffer jump with no jump cued
            self.buffer_dash = False
            self.dashbuff_timer = self.dashbuff_max
        # - kill -
        # if not dashing or timer exceeded, end dash but don't reset timer (prevents multiple dashes in the air)
        else:
            self.dashing = False

        # -- buffer dash timer --
        # cue up dash if dash button pressed (if dash is already allowed it will be maxed out in the dash code)
        # OR having already cued, continue timing
        if (self.dashbuff_timer == 0) or self.buffer_dash:
            self.dashbuff_timer += round(1 * dt)
            self.buffer_dash = True

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
    def apply_y_direction(self, dt):
        y_move = round(self.direction.y * dt)

        self.rect.y += y_move
        self.sync_hitbox()

        for circle in self.circles:
            circle[1][1] += y_move

    # syncs the player's current and stored hitboxes with the player rect for proper collisions. For use after movement of player rect.
    def sync_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    # syncs the player's rect with the current hitbox for proper movement. For use after movement of main hitbox
    def sync_rect(self):
        self.rect.midbottom = self.hitbox.midbottom

    def update(self, mouse_pos, dt, tiles):
        self.sync_hitbox()  # just in case

        # -- INPUT --
        self.get_input(dt, tiles)
        self.rect.centerx = mouse_pos[0]//scaling_factor
        self.rect.centery = mouse_pos[1]//scaling_factor

        r_circles = []
        for circle in range(len(self.circles)):
            self.circles[circle][0] -= 0.8
            if self.circles[circle][0] < self.smallest_circle:
                r_circles.append(circle)
        for circle in r_circles:
            self.circles.pop(circle)
        self.circles.append([self.start_radius, [self.rect.centerx, self.rect.centery]])

        # -- CHECKS/UPDATE --

        # - collision and movement -
        # applies direction to player then resyncs hitbox (included in most movement/collision functions)
        # HITBOX MUST BE SYNCED AFTER EVERY MOVE OF PLAYER RECT
        # x and y collisions are separated to make diagonal collisions easier and simpler to handle
        # x
        self.apply_x_direction(dt)
        self.collision_x(self.hitbox, tiles)

        # y
        # applies direction to player then resyncs hitbox
        self.apply_y_direction(dt)  # gravity
        self.collision_y(self.hitbox, tiles)

        # light (after movement and scroll so pos is accurate)
        for light in self.lights:
            light.update(dt, self.rect.center, tiles)

# -- visual methods --

    def draw(self):
        for light in self.lights:
            light.draw()

        for circle in self.circles:
            pygame.draw.circle(self.surface, 'red', circle[1], circle[0])

