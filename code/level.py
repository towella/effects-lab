# - libraries -
import pygame
from pytmx.util_pygame import load_pygame  # allows use of tiled tile map files for pygame use
# - general -
from game_data import tile_size, controls, fonts
from support import *
# - tiles -
from tiles import CollideableTile, HazardTile
# - objects -
from player import Player
from trigger import Trigger
from spawn import Spawn
from menus import Drag_Menu
# - systems -
from text import Font


class Level:
    def __init__(self, mouse_pos, screen_surface, screen_rect):
        # level setup
        self.screen_surface = screen_surface  # main screen surface
        self.screen_rect = screen_rect
        self.screen_width = screen_surface.get_width()
        self.screen_height = screen_surface.get_height()

        self.mask_surf = pygame.Surface((self.screen_width, self.screen_height))
        self.mask_surf.set_colorkey((0, 0, 0))

        # -- Menus --
        # - Pause -
        self.pause = False
        self.pause_pressed = False
        # - Settings -
        self.settings = False
        self.settings_pressed = False
        # - Controls -
        menu_y_pos = self.screen_surface.get_height()  # y pos of menu bg
        height = 20  # height of button
        width = 50  # width of button
        centered_x = center_object_x(width, self.screen_surface.get_width())  # coord for centering button on x
        y_pos = menu_y_pos - height//2  # coord for button on y
        self.controls_m = Drag_Menu("../assets/menus/controls", self.screen_surface,
                                    pygame.Rect(centered_x, y_pos, width, height), (0, menu_y_pos))

        dt = 1  # dt starts as 1 because on the first frame we can assume it is 60fps. dt = 1/60 * 60 = 1

        self.player = Player(mouse_pos, self.mask_surf)

        # text setup
        self.small_font = Font(resource_path(fonts['small_font']), 'white')
        self.large_font = Font(resource_path(fonts['large_font']), 'white')

# -- set up room methods --

    # creates all the neccessary types of tiles seperately and places them in individual layer groups
    def create_tile_group(self, tmx_file, layer, type):
        sprite_group = pygame.sprite.Group()

        if type == 'CollideableTile':
            # gets layer from tmx and creates StaticTile for every tile in the layer, putting them in both SpriteGroups
            for x, y, surface in tmx_file.get_layer_by_name(layer).tiles():
                tile = CollideableTile((x * tile_size, y * tile_size), tile_size, surface)
                sprite_group.add(tile)
                self.all_sprites.add(tile)
        elif type == 'HazardTile':
            for x, y, surface in tmx_file.get_layer_by_name(layer).tiles():
                tile = HazardTile((x * tile_size, y * tile_size), tile_size, surface, self.player.sprite)
                sprite_group.add(tile)
                self.all_sprites.add(tile)
        else:
            raise Exception(f"Invalid create_tile_group type: '{type}' ")

        return sprite_group

    def create_object_group(self, tmx_file, layer, object):
        sprite_group = pygame.sprite.Group()
        if object == 'Trigger':
            for obj in tmx_file.get_layer_by_name(layer):  # can iterate over for objects
                # checks if object is a trigger (multiple objects could be in the layer
                if obj.type == 'trigger':
                    trigger = Trigger(obj.x, obj.y, obj.width, obj.height, obj.name)
                    sprite_group.add(trigger)
                    self.all_sprites.add(trigger)
        elif object == 'Spawn':
            sprite_group = {}
            for obj in tmx_file.get_layer_by_name(layer):
                # multiple types of object could be in layer, so checking it is correct object type (spawn)
                if obj.type == 'spawn':
                    # creates a dictionary containing spawn name: spawn pairs for ease and efficiency of access
                    spawn = Spawn(obj.x, obj.y, obj.name, obj.player_facing)
                    sprite_group[spawn.name] = spawn
                    self.all_sprites.add(spawn)
        elif object == 'Player':
            sprite_group = pygame.sprite.GroupSingle()
            # finds the correct starting position corresponding to the last room/transition
            spawn = (0, 0)
            player = Player(spawn, self.screen_surface)
            sprite_group.add(player)
        else:
            raise Exception(f"Invalid create_object_group type: '{type}' ")

        return sprite_group

# -- check methods --

    def get_input(self):
        keys = pygame.key.get_pressed()

        # pause menu
        if keys[controls["Pause"]]:
            if not self.pause_pressed:
                self.pause = not self.pause
            self.pause_pressed = True
        else:
            self.pause_pressed = False

        # settings menu
        if keys[controls["Settings"]]:
            if not self.settings_pressed:
                self.settings = not self.settings
            self.settings_pressed = True
        else:
            self.settings_pressed = False

# -- visual --

    # draw tiles in tile group but only if in camera view (in tile.draw method)
    def draw_tile_group(self, group):
        for tile in group:
            # render tile
            tile.draw(self.screen_surface, self.screen_rect)

    def make_mask(self):
        mask = pygame.mask.from_surface(self.mask_surf)
        mask = mask.to_surface()
        mask.set_colorkey((255, 255, 255))
        mask = outline_image(mask, 'black')
        return mask

# -- menus --

    def invoke_pause(self):
        self.pause = True

    def pause_menu(self):
        pause_surf = pygame.Surface((self.screen_surface.get_width(), self.screen_surface.get_height()))
        pause_surf.fill((20, 20, 20))
        self.screen_surface.blit(pause_surf, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
        txt_surf = self.large_font.get_surf('PAUSED', 'black')
        self.screen_surface.blit(txt_surf, (center_object_x_surf(txt_surf, self.screen_surface), 20))
        #self.large_font.render('PAUSED', self.screen_surface, (center_object_x_surf(width, self.screen_surface), 20))

    def settings_menu(self):
        pass

# -------------------------------------------------------------------------------- #

    # updates the level allowing tile scroll and displaying tiles to screen
    # order is equivalent of layers
    def update(self, dt, mouse_pos):
        # #### INPUT > GAME(checks THEN UPDATE) > RENDER ####
        # checks deal with previous frames interactions. Update creates interactions for this frame which is then diplayed
        '''player = self.player.sprite'''

        # -- INPUT --
        self.get_input()

        # -- CHECKS (For the previous frame)  --
        if not self.pause:
            # which object should handle collision? https://gamedev.stackexchange.com/questions/127853/how-to-decide-which-gameobject-should-handle-the-collision

            # checks if player has collided with spawn trigger and updates spawn
            '''for trigger in self.spawn_triggers:
                if player.hitbox.colliderect(trigger.hitbox):
                    self.player_spawn = self.player_spawns[trigger.name]
                    break'''

            # checks if the player needs to respawn and therefore needs to focus on the player
            '''if player.get_respawn():
                self.camera.focus(True)'''

            # checks which collideable tiles are in screen view.
            # TODO in function? More tile layers included? Use for tile rendering? IF ADD MORE LAYERS, CHANGE PLAYER TILES COLLISION LAYER
            '''self.tiles_in_screen = []
            for tile in self.collideable:
                if tile.hitbox.colliderect(self.screen_rect):
                    self.tiles_in_screen.append(tile)'''

        # -- UPDATES -- player needs to be before tiles for scroll to function properly
            # TODO IF TILES_IN_SCREEN ATTR IS CHANGED TO INCLUDE MORE LAYERS, CHANGE BACK TO self.collideable HERE!!!!
            self.player.update(mouse_pos, dt, pygame.sprite.Group())
            '''self.all_sprites.update(scroll_value)'''

            self.controls_m.update(mouse_pos)

        # -- RENDER -- (back --> front)
        # Draw
        self.player.draw()
        '''self.draw_tile_group(self.collideable)
        self.draw_tile_group(self.hazards)'''

        self.screen_surface.blit(self.make_mask(), (-1, -1))
        self.mask_surf.fill('black')
        self.mask_surf.set_colorkey('black')

        self.controls_m.draw()

        if self.pause:
            self.pause_menu()

        # player cursor
        cursor = circle_surf(3, 'black')
        cursor = outline_image(cursor, 'white', 2)
        cursor_pos = pos_for_center(cursor, mouse_pos)
        self.screen_surface.blit(cursor, cursor_pos)
