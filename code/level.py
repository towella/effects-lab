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
from menus import *
from interactives import Button
# - systems -
from text import Font


class Level:
    def __init__(self, mouse_pos, screen_surface, screen_rect):
        # level setup
        self.screen_surface = screen_surface  # main screen surface
        self.screen_rect = screen_rect
        self.screen_width = screen_surface.get_width()
        self.screen_height = screen_surface.get_height()

        # fullscreen (should really be in main but I need it in settings menu and its easier if its here)
        self.fullscreen = True
        self.fullscreen_pressed = False

        self.mask_surf = pygame.Surface((self.screen_width, self.screen_height))
        self.mask_surf.set_colorkey((0, 0, 0))

        self.sound = True

        # -- Menus --
        # - Pause -
        self.pause = False
        self.pause_pressed = False
        # - Settings -
        self.settings = False
        self.settings_pressed = False
        self.settings_b = Button((self.screen_surface.get_width() - 27, 5), (22, 22), "../assets/buttons/settings",
                                 (0, 0), False)
        self.settings_menu = Settings_Menu("../assets/menus/settings", self.screen_surface, 20)
        # - Info -
        self.info_b = Button((5, 5), (22, 22), "../assets/buttons/info", (0, 0), False)
        self.info = False
        self.info_menu = Info_Menu("../assets/menus/info", self.screen_surface, 20)
        # - Controls -
        self.activate_controls_m = False
        self.activate_controls_pressed = False
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

# -- check methods --

    def settings_io(self):
        if self.settings:
            self.settings_menu.reset_menu({"bloom": self.player.tail_bloom, "gravity": self.player.apply_gravity,
                                           "flame": self.player.apply_flame, "blast": self.player.allow_hold_click,
                                           "fullscreen": self.fullscreen,
                                           "tail length/bloom speed": self.player.subtract_r,
                                           "flame volume": self.player.flame_volume, "flame amplitude": self.player.flame_amplitude,
                                           "flame rate": self.player.flame_speed,
                                           "blast width": self.player.blast_width, "blast speed": self.player.blast_speed,
                                           "blast duration": self.player.blast_duration, "screen shake": self.player.apply_screen_shake,
                                           "shake duration": self.player.screen_shake_max, "shake intensity": self.player.max_screen_shake})
        else:
            values = self.settings_menu.get_values()
            self.player.tail_bloom = values["bloom"]
            self.player.apply_gravity = values["gravity"]
            self.player.apply_flame = values["flame"]
            self.player.allow_hold_click = values["blast"]
            self.fullscreen = values["fullscreen"]

            self.player.subtract_r = values["tail length/bloom speed"]

            self.player.flame_volume = values["flame volume"]
            self.player.flame_amplitude = values["flame amplitude"]
            self.player.flame_speed = values["flame rate"]

            self.player.blast_width = values["blast width"]
            self.player.blast_speed = values["blast speed"]
            self.player.blast_duration = values["blast duration"]

            self.player.apply_screen_shake = values["screen shake"]
            self.player.screen_shake_max = values["shake duration"]
            self.player.max_screen_shake = values["shake intensity"]

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_TAB] and not self.settings and not self.info:
            if not self.fullscreen_pressed:
                pygame.display.toggle_fullscreen()
                self.pause = True
                self.fullscreen_pressed = True
                self.fullscreen = not self.fullscreen
        else:
            self.fullscreen_pressed = False

        # pause menu
        if keys[controls["Pause"]] and not self.settings and not self.info:
            if not self.pause_pressed:
                self.pause = not self.pause
            self.pause_pressed = True
        else:
            self.pause_pressed = False

        # settings menu
        if keys[controls["Settings"]] and not self.pause and not self.info:
            if not self.settings_pressed:
                self.settings = not self.settings
                self.settings_io()
            self.settings_pressed = True
        else:
            self.settings_pressed = False

        # bring up/down controls menu
        if keys[controls["Controls"]] and not self.activate_controls_pressed and not self.pause and not self.settings and not self.info:
            self.activate_controls_pressed = True
            # if was active, make inactive
            if self.activate_controls_m:
                self.controls_m.rect.top = self.screen_surface.get_height()
                self.controls_m.drag_button.hitbox.centery = self.screen_surface.get_height()
            # vice versa
            else:
                self.controls_m.rect.top = 0
                self.controls_m.drag_button.hitbox.centery = 0
            self.activate_controls_m = not self.activate_controls_m
        elif not keys[controls["Controls"]]:
            self.activate_controls_pressed = False

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

# -------------------------------------------------------------------------------- #

    def get_screen_shake(self):
        return self.player.get_screen_shake()

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
            if not self.settings and not self.info:
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

                # - Controls menu -
                self.controls_m.update(mouse_pos)
                # allow menu state to change based on drag as well as hotkey
                if self.controls_m.rect.top < self.screen_surface.get_height():
                    self.activate_controls_m = True
                else:
                    self.activate_controls_m = False

            # - Settings button -
            self.settings_b.update(mouse_pos)
            if self.settings_b.get_activated() and not self.info:
                self.settings = not self.settings
                self.settings_io()
            elif self.settings_b.get_hover(mouse_pos):
                self.player.screen_shake_timer = 0
                self.player.screen_shake = [0, 0]

            # - Settings menu -
            if self.settings:
                self.settings_menu.update(mouse_pos)
                if self.settings_menu.get_close() and self.settings:
                    self.settings = False
                    self.settings_io()

            # - Info button -
            self.info_b.update(mouse_pos)
            if self.info_b.get_activated() and not self.settings:
                self.info = not self.info
                self.info_menu.update(mouse_pos)
            elif self.info_b.get_hover(mouse_pos):
                self.player.screen_shake_timer = 0
                self.player.screen_shake = [0, 0]

            if self.info:
                self.info_menu.update(mouse_pos)
                if self.info_menu.get_close() and self.info:
                    self.info = False
                    self.info_menu.reset()

        # -- RENDER -- (back --> front)
        # Draw
        self.player.draw()
        '''self.draw_tile_group(self.collideable)
        self.draw_tile_group(self.hazards)'''

        self.screen_surface.blit(self.make_mask(), (-1, -1))
        self.mask_surf.fill('black')
        self.mask_surf.set_colorkey('black')

        self.settings_b.draw(self.screen_surface)
        self.info_b.draw(self.screen_surface)

        self.controls_m.draw()

        if self.settings:
            pause_surf = pygame.Surface((self.screen_surface.get_width(), self.screen_surface.get_height()))
            pause_surf.fill((20, 20, 20))
            self.screen_surface.blit(pause_surf, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            self.settings_menu.draw()
        elif self.info:
            pause_surf = pygame.Surface((self.screen_surface.get_width(), self.screen_surface.get_height()))
            pause_surf.fill((20, 20, 20))
            self.screen_surface.blit(pause_surf, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            self.info_menu.draw()

        if self.pause:
            self.pause_menu()

        # player cursor
        cursor = circle_surf(3, 'black')
        cursor = outline_image(cursor, 'white', 2)
        cursor_pos = pos_for_center(cursor, mouse_pos)
        self.screen_surface.blit(cursor, cursor_pos)
