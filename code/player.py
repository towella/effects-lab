import pygame
from game_data import tile_size, controller_map, scaling_factor
from random import randint
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
        self.subtract_r = 0.4

        # - hitbox -
        self.hitbox = pygame.Rect(spawn[0], spawn[1], self.start_radius, self.start_radius)

        self.respawn = False

        # -- player movement --
        self.direction = pygame.math.Vector2(0, 0)  # allows cleaner movement by storing both x and y direction
        # collisions -- provides a buffer allowing late collision
        self.collision_tolerance = tile_size
        self.corner_correction = 8  # tolerance for correcting player on edges of tiles (essentially rounded corners)

        self.gravity = 2
        self.apply_gravity = False
        self.gravity_pressed = False

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

    def get_input(self, click, dt, tiles):
        self.direction.x = 0
        keys = pygame.key.get_pressed()

        # tail size
        if keys[pygame.K_m]:
            self.subtract_r += 0.05 * dt
        if keys[pygame.K_n]:
            self.subtract_r -= 0.05 * dt

        # gravity
        if keys[pygame.K_g] and not self.gravity_pressed:
            self.apply_gravity = not self.apply_gravity
            self.gravity_pressed = True
        elif not keys[pygame.K_g]:
            self.gravity_pressed = False

        if self.subtract_r < 0:
            self.subtract_r = 0

        # blobs
        if click:
            # randomly decide how many blob streaks will be created
            for i in range(randint(3, 6)):
                self.blob()  # make blob streaks


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
    def apply_y_direction(self, dt):
        for circle in range(len(self.circles)):
            self.circles[circle][1][1] += round(self.gravity * dt)

    # syncs the player's current and stored hitboxes with the player rect for proper collisions. For use after movement of player rect.
    def sync_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    # syncs the player's rect with the current hitbox for proper movement. For use after movement of main hitbox
    def sync_rect(self):
        self.rect.midbottom = self.hitbox.midbottom

    def update(self, mouse_pos, click, dt, tiles):
        self.sync_hitbox()  # just in case

        # -- INPUT --
        self.get_input(click, dt, tiles)
        self.rect.centerx = mouse_pos[0]//scaling_factor
        self.rect.centery = mouse_pos[1]//scaling_factor

        r_circles = []
        for circle in range(len(self.circles)):
            self.circles[circle][0] -= self.subtract_r * dt
            if self.circles[circle][0] < self.smallest_circle:
                r_circles.append(self.circles[circle])
        for circle in r_circles:
            self.circles.remove(circle)
        self.circles.append([self.start_radius, [self.rect.centerx, self.rect.centery]])

        if self.apply_gravity:
            self.apply_y_direction(dt)

        # -- CHECKS/UPDATE --

        # - collision and movement -
        # applies direction to player then resyncs hitbox (included in most movement/collision functions)
        # HITBOX MUST BE SYNCED AFTER EVERY MOVE OF PLAYER RECT
        # x and y collisions are separated to make diagonal collisions easier and simpler to handle
        self.collision_x(self.hitbox, tiles)
        self.collision_y(self.hitbox, tiles)

# -- visual methods --

    def blob(self):
        angle = randint(1, 360)  # pick a random angle
        max_distance = randint(10, 30)


    def draw(self):
        for circle in self.circles:
            pygame.draw.circle(self.surface, 'red', circle[1], circle[0])

