import pygame
from game_data import controls, fonts, version, release
from support import resource_path, import_folder, center_object_x_surf, center_object_x
from text import Font
from interactives import *

# PLEASE DO NOT RE USE THESE CLASSES!!! THEY ARE POORLY WRITTEN AND SPECIFIC TO THIS PROJECT!
# REWRITE MENU CLASS TO INCLUDE PAGE CLASS AS WELL

class Drag_Menu(pygame.sprite.Sprite):
    def __init__(self, path, surface, drag_rect, menu_pos):
        super().__init__()
        resources = import_folder(path)
        self.surface = surface
        self.img = resources["background"]
        self.rect = self.img.get_rect()
        self.rect.topleft = menu_pos
        self.drag_button = Button(drag_rect.topleft, (drag_rect.width, drag_rect.height), path + "/drag_button", (0, 0), False)
        self.button_down = False

        # fonts
        self.small_font = Font(fonts['small_font'], 'black')
        self.large_font = Font(fonts['large_font'], 'white')

        # Setup menu text on image
        title = self.large_font.get_surf("Controls", "black")
        self.img.blit(title, (center_object_x_surf(title, self.img), 15))

        x = 10  # starting padding
        y = 40  # starting padding
        rows = 7
        columns = 3
        index = 0
        keys = list(controls)
        for j in range(rows):
            for k in range(columns):
                key = keys[index]
                # if key, convert int value to corresponding character (uppercased)
                if isinstance(controls[key], int):
                    value = chr(int(controls[key])).upper()
                # otherwise use non numerical value in text
                else:
                    value = controls[key]
                # get correct text format
                if "+/-" in key:
                    text = self.small_font.get_surf(f"{key} - {value}/{value}+Shift")
                else:
                    text = self.small_font.get_surf(f"{key} - {value}")
                text = outline_image(text, 'white')
                self.img.blit(text, (x, y))
                x += (self.surface.get_width() - 30) // columns + 20

                index += 1
                # -1 because len counts from 1 rather than 0
                # prevents index becoming out of range
                if len(keys) - 1 < index:
                    break

            x = 10
            y += (self.surface.get_height() - 20) // rows

            # -1 because len counts from 1 rather than 0
            # prevents index becoming out of range
            if len(keys) - 1 < index:
                break

    # This is so bodgy I am so sorry
    def update(self, mouse_pos):
        self.drag_button.update(mouse_pos)

        # if player clicks in button, button down is true and allow drag
        if pygame.mouse.get_pressed()[0] and self.drag_button.hitbox.collidepoint(mouse_pos):
            self.button_down = True
        # otherwise disallow drag because player is not clicking
        # This allows the player to move out of the button hitbox and still drag, allowing faster dragging, snapping to mouse
        elif not pygame.mouse.get_pressed()[0]:
            self.button_down = False

        if self.button_down:
            prev_y = self.drag_button.hitbox.centery
            self.drag_button.hitbox.centery = mouse_pos[1] + 1  # +1 to offset from mouse (allow menu flush with bottom screen)
            self.rect.y += self.drag_button.hitbox.centery - prev_y

    def draw(self):
        self.surface.blit(self.img, self.rect.topleft)
        self.drag_button.draw(self.surface)


class Settings_Menu:
    def __init__(self, path, surface, y_pos):
        resources = import_folder(path)
        self.surface = surface
        self.img = resources["background"]
        self.working_surf = self.img.copy()
        self.rect = self.img.get_rect()
        self.values = {}

        self.close = False

        # get menu pos with menu centered on x
        width = self.rect.width
        centered_x = center_object_x(width, self.surface.get_width())
        self.rect.topleft = (centered_x, y_pos)

        # buttons
        self.interactives = {}

        # fonts
        self.small_font = Font(fonts['small_font'], 'black')
        self.large_font = Font(fonts['large_font'], 'white')

        self.page = ""
        self.setup_main_page()

    def reset_menu(self, vals_dict):
        self.close = False
        self.set_values(vals_dict)
        self.setup_main_page()

    def clear_page(self, title):
        self.page = title
        self.interactives = {}
        self.working_surf = self.img.copy()

    # -- Page Setup --

    def setup_main_page(self):
        self.clear_page("main")

        # Setup menu text on image
        title = self.large_font.get_surf("Settings", "black")
        self.working_surf.blit(title, (center_object_x_surf(title, self.working_surf), 10))

        # -- Buttons --
        self.interactives["close"] = Button((self.rect.topleft[0] + 10, self.rect.topleft[1] + 10), (9, 10),
                                            "../assets/menus/settings/pages/main/close_button", (0, 0), False)

        top_left = self.rect.topleft
        height = 42
        y_increment = 47
        y = 35

        width = 85
        center_x = center_object_x(width, self.surface.get_width())
        self.interactives["toggles"] = Button((center_x, top_left[1] + y), (width, height),
                                              "../assets/menus/settings/pages/main/toggles_button", (0, 0), False)

        y += y_increment
        width = 109
        center_x = center_object_x(width, self.surface.get_width())
        self.interactives["tail"] = Button((center_x, top_left[1] + y), (width, height),
                                           "../assets/menus/settings/pages/main/tail_modifiers_button", (0, 0), False)

        y += y_increment
        width = 123
        center_x = center_object_x(width, self.surface.get_width())
        self.interactives["flame"] = Button((center_x, top_left[1] + y), (width, height),
                                            "../assets/menus/settings/pages/main/flame_modifiers_button", (0, 0), False)

        y += y_increment
        width = 120
        center_x = center_object_x(width, self.surface.get_width())
        self.interactives["blast"] = Button((center_x, top_left[1] + y), (width, height),
                                            "../assets/menus/settings/pages/main/blast_modifiers_button", (0, 0), False)

        # bottom disclaimer
        text = self.small_font.get_surf("Use of keyboard shortcuts is recommended for best user experience")
        self.working_surf.blit(text, (center_object_x_surf(text, self.working_surf), self.rect.bottom - 38))

    def setup_toggles_page(self):
        self.clear_page("toggles")

        # Setup menu text on image
        title = self.large_font.get_surf("Toggles", "black")
        self.working_surf.blit(title, (center_object_x_surf(title, self.working_surf), 10))

        # -- Buttons --
        self.interactives["back"] = Button((self.rect.topleft[0] + 10, self.rect.topleft[1] + 10), (9, 10),
                                           "../assets/menus/settings/pages/toggles/back_button", (0, 0), False)

        # -- Switches --
        y_increment = 26
        y = self.rect.topleft[1] + 30
        switch_width = 26
        switch_height = 13
        switch_path = "../assets/menus/settings/pages/toggles/switch"

        text = self.small_font.get_surf("Tail Bloom: ")
        center_x = center_object_x(text.get_width() + switch_width, self.working_surf.get_width())
        if self.values["bloom"] == 1:
            toggle = False
        else:
            toggle = True
        self.interactives["bloom"] = Toggle(toggle,
                                            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
                                            (switch_width, switch_height),
                                            switch_path, (0, 0), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Tail Gravity: ")
        center_x = center_object_x(text.get_width() + switch_width, self.working_surf.get_width())
        self.interactives["gravity"] = Toggle(self.values["gravity"],
                                           (self.rect.topleft[0] + center_x + text.get_width(),
                                            self.rect.topleft[1] + y - 3),
                                           (switch_width, switch_height),
                                           switch_path, (0, 0), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Flame: ")
        center_x = center_object_x(text.get_width() + switch_width, self.working_surf.get_width())
        self.interactives["flame"] = Toggle(self.values["flame"],
                                              (self.rect.topleft[0] + center_x + text.get_width(),
                                               self.rect.topleft[1] + y - 3),
                                              (switch_width, switch_height),
                                              switch_path, (0, 0), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Repeat Radial Blast: ")
        center_x = center_object_x(text.get_width() + switch_width, self.working_surf.get_width())
        self.interactives["blast"] = Toggle(self.values["blast"],
                                            (self.rect.topleft[0] + center_x + text.get_width(),
                                            self.rect.topleft[1] + y - 3), (switch_width, switch_height),
                                            switch_path, (0, 0), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Screen Shake: ")
        center_x = center_object_x(text.get_width() + switch_width, self.working_surf.get_width())
        self.interactives["screen shake"] = Toggle(self.values["screen shake"],
                                            (self.rect.topleft[0] + center_x + text.get_width(),
                                             self.rect.topleft[1] + y - 3), (switch_width, switch_height),
                                            switch_path, (0, 0), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Fullscreen: ")
        center_x = center_object_x(text.get_width() + switch_width, self.working_surf.get_width())
        self.interactives["fullscreen"] = Toggle(self.values["fullscreen"],
                                            (self.rect.topleft[0] + center_x + text.get_width(),
                                             self.rect.topleft[1] + y - 3),
                                            (switch_width, switch_height),
                                            switch_path, (0, 0), False)
        self.working_surf.blit(text, (center_x, y))

    def setup_tail_page(self):
        self.clear_page("tail")

        # Setup menu text on image
        title = self.large_font.get_surf("Tail Modifiers", "black")
        self.working_surf.blit(title, (center_object_x_surf(title, self.working_surf), 10))

        # -- Buttons --
        self.interactives["back"] = Button((self.rect.topleft[0] + 10, self.rect.topleft[1] + 10), (9, 10),
                                            "../assets/menus/settings/pages/tail/back_button", (0, 0), False)

        # -- Sliders --
        y_increment = 26
        y = self.rect.topleft[1] + 25
        slider_width = 51
        slider_path = "../assets/menus/settings/pages/tail/slider"

        text = self.small_font.get_surf("Tail Length/Bloom Speed: ")
        value = self.small_font.get_surf("  " + str(int(self.values["tail length/bloom speed"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["tail length/bloom speed"] = Slider((self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
                                                              (slider_width, 13), 1, 3, self.values["tail length/bloom speed"],
                                                              self.rect.topleft[1] + y - 3, (7, 13),
                                                              slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

    def setup_flame_page(self):
        self.clear_page("flame")

        # Setup menu text on image
        title = self.large_font.get_surf("Flame Modifiers", "black")
        self.working_surf.blit(title, (center_object_x_surf(title, self.working_surf), 10))

        # -- Buttons --
        self.interactives["back"] = Button((self.rect.topleft[0] + 10, self.rect.topleft[1] + 10), (9, 10),
                                            "../assets/menus/settings/pages/flame/back_button", (0, 0), False)

        # -- Sliders --
        y_increment = 26
        y = self.rect.topleft[1] + 25
        slider_width = 51
        slider_path = "../assets/menus/settings/pages/flame/slider"

        text = self.small_font.get_surf("Flame Volume: ")
        value = self.small_font.get_surf("  " + str(int(self.values["flame volume"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["flame volume"] = Slider(
            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
            (slider_width, 13), 1, 2, self.values["flame volume"],
            self.rect.topleft[1] + y - 3, (7, 13),
            slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Flame Amplitude: ")
        value = self.small_font.get_surf("  " + str(int(self.values["flame amplitude"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["flame amplitude"] = Slider(
            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
            (slider_width, 13), 1, 2, self.values["flame amplitude"],
            self.rect.topleft[1] + y - 3, (7, 13),
            slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Flame Rate: ")
        value = self.small_font.get_surf("  " + str(int(self.values["flame rate"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["flame rate"] = Slider(
            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
            (slider_width, 13), 1, 8, self.values["flame rate"],
            self.rect.topleft[1] + y - 3, (7, 13),
            slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

    def setup_blast_page(self):
        self.clear_page("blast")

        # Setup menu text on image
        title = self.large_font.get_surf("Blast Modifiers", "black")
        self.working_surf.blit(title, (center_object_x_surf(title, self.working_surf), 10))

        # -- Buttons --
        self.interactives["back"] = Button((self.rect.topleft[0] + 10, self.rect.topleft[1] + 10), (9, 10),
                                            "../assets/menus/settings/pages/blast/back_button", (0, 0), False)

        # -- Sliders --
        y_increment = 26
        y = self.rect.topleft[1] + 25
        slider_width = 51
        slider_path = "../assets/menus/settings/pages/blast/slider"

        text = self.small_font.get_surf("Blast Speed: ")
        value = self.small_font.get_surf("  " + str(int(self.values["blast speed"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["blast speed"] = Slider(
            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
            (slider_width, 13), 1, 20, self.values["blast speed"],
            self.rect.topleft[1] + y - 3, (7, 13),
            slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Blast Width: ")
        value = self.small_font.get_surf("  " + str(int(self.values["blast width"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["blast width"] = Slider(
            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
            (slider_width, 13), 1, 10, self.values["blast width"],
            self.rect.topleft[1] + y - 3, (7, 13),
            slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Blast Duration: ")
        value = self.small_font.get_surf("  " + str(int(self.values["blast duration"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["blast duration"] = Slider(
            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
            (slider_width, 13), 1, 8, self.values["blast duration"],
            self.rect.topleft[1] + y - 3, (7, 13),
            slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

        # ------------ SCREEN SHAKE ------------------------
        y += y_increment * 1.5
        # Setup menu text on image
        title = self.large_font.get_surf("Screen Shake Modifiers", "black")
        self.working_surf.blit(title, (center_object_x_surf(title, self.working_surf), y))

        y += y_increment
        text = self.small_font.get_surf("Screen Shake Duration: ")
        value = self.small_font.get_surf("  " + str(int(self.values["shake duration"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["shake duration"] = Slider(
            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
            (slider_width, 13), 1, 4, self.values["shake duration"],
            self.rect.topleft[1] + y - 3, (7, 13),
            slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

        y += y_increment
        text = self.small_font.get_surf("Screen Shake Intensity: ")
        value = self.small_font.get_surf("  " + str(int(self.values["shake intensity"])))
        center_x = center_object_x(text.get_width() + slider_width + value.get_width(), self.working_surf.get_width())
        self.interactives["shake intensity"] = Slider(
            (self.rect.topleft[0] + center_x + text.get_width(), self.rect.topleft[1] + y - 3),
            (slider_width, 13), 1, 4, self.values["shake intensity"],
            self.rect.topleft[1] + y - 3, (7, 13),
            slider_path, (0, 0), (0, 6), False)
        self.working_surf.blit(text, (center_x, y))

    # -- Page Checks --

    def main_page(self):
        # close if button is pressed
        if self.interactives["close"].get_activated():
            self.close = True

        # - change page buttons -
        if self.interactives["toggles"].get_activated():
            self.setup_toggles_page()
        elif self.interactives["tail"].get_activated():
            self.setup_tail_page()
        elif self.interactives["flame"].get_activated():
            self.setup_flame_page()
        elif self.interactives["blast"].get_activated():
            self.setup_blast_page()

    def toggles_page(self):
        # back button
        if self.interactives["back"].get_activated():
            self.setup_main_page()

        elif self.interactives["bloom"].get_activated():
            if self.interactives["bloom"].get_toggle():
                self.values["bloom"] = -1
            else:
                self.values["bloom"] = 1
        elif self.interactives["blast"].get_activated():
            self.values["blast"] = self.interactives["blast"].get_toggle()
        elif self.interactives["screen shake"].get_activated():
            self.values["screen shake"] = self.interactives["screen shake"].get_toggle()
        elif self.interactives["fullscreen"].get_activated():
            self.values["fullscreen"] = self.interactives["fullscreen"].get_toggle()
            pygame.display.toggle_fullscreen()

        # flame and gravity can not be on at the same time. Turn one off if the other is clicked
        elif self.interactives["gravity"].get_toggle() and self.interactives["flame"].get_activated():
            self.interactives["gravity"].set_toggle(False)
            self.values["gravity"] = False
            self.values["flame"] = True
        elif self.interactives["flame"].get_activated():
            self.values["flame"] = self.interactives["flame"].get_toggle()
        elif self.interactives["flame"].get_toggle() and self.interactives["gravity"].get_activated():
            self.interactives["flame"].set_toggle(False)
            self.values["flame"] = False
            self.values["gravity"] = True
        elif self.interactives["gravity"].get_activated():
            self.values["gravity"] = self.interactives["gravity"].get_toggle()

    def tail_page(self):
        # -- UPDATE --
        if self.interactives["back"].get_activated():
            self.setup_main_page()

        elif self.interactives["tail length/bloom speed"].get_activated():
            self.values["tail length/bloom speed"] = self.interactives["tail length/bloom speed"].get_value()

    def flame_page(self):
        if self.interactives["back"].get_activated():
            self.setup_main_page()

        elif self.interactives["flame volume"].get_activated():
            self.values["flame volume"] = self.interactives["flame volume"].get_value()
        elif self.interactives["flame amplitude"].get_activated():
            self.values["flame amplitude"] = self.interactives["flame amplitude"].get_value()
        elif self.interactives["flame rate"].get_activated():
            self.values["flame rate"] = self.interactives["flame rate"].get_value()

    def blast_page(self):
        if self.interactives["back"].get_activated():
            self.setup_main_page()

        elif self.interactives["blast width"].get_activated():
            self.values["blast width"] = self.interactives["blast width"].get_value()
        elif self.interactives["blast speed"].get_activated():
            self.values["blast speed"] = self.interactives["blast speed"].get_value()
        elif self.interactives["blast duration"].get_activated():
            self.values["blast duration"] = self.interactives["blast duration"].get_value()

        elif self.interactives["shake duration"].get_activated():
            self.values["shake duration"] = self.interactives["shake duration"].get_value()
        elif self.interactives["shake intensity"].get_activated():
            self.values["shake intensity"] = self.interactives["shake intensity"].get_value()

    # ---------------------

    def draw_slider_page(self):
        # -- DRAW --
        for key in self.interactives:
            element = self.interactives[key]
            if isinstance(element, Slider):
                text = self.small_font.get_surf("  " + str(int(self.values[key])))
                self.surface.blit(text, (element.bar_rect.topright[0], element.bar_rect.topright[1] + 3))

    # -- Get attrs --

    def get_close(self):
        return self.close

    def set_values(self, val_dict):
        self.values = val_dict

    def get_values(self):
        return self.values

    # returns if settings menu should be up or not
    def update(self, mouse_pos):
        # update page buttons
        for button in self.interactives:
            self.interactives[button].update(mouse_pos)

        # allow pages to do stuff with buttons
        if self.page == "main":
            self.main_page()
        elif self.page == "toggles":
            self.toggles_page()
        elif self.page == "flame":
            self.flame_page()
        elif self.page == "tail":
            self.tail_page()
        elif self.page == "blast":
            self.blast_page()

    def draw(self):
        self.surface.blit(self.working_surf, self.rect.topleft)

        for button in self.interactives:
            self.interactives[button].draw(self.surface)

        if self.page in "tail flame blast":
            self.draw_slider_page()


class Info_Menu:
    def __init__(self, path, surface, y_pos):
        resources = import_folder(path)
        self.surface = surface
        self.img = resources["background"]
        self.working_surf = self.img.copy()
        self.rect = self.img.get_rect()
        self.values = {}

        self.close = False

        # get menu pos with menu centered on x
        width = self.rect.width
        centered_x = center_object_x(width, self.surface.get_width())
        self.rect.topleft = (centered_x, y_pos)

        # buttons
        self.interactives = {}

        # fonts
        self.small_font = Font(fonts['small_font'], 'black')
        self.large_font = Font(fonts['large_font'], 'white')

        self.page = ""
        self.setup_main_page()

    def get_close(self):
        return self.close

    def setup_main_page(self):
        # Setup menu text on image
        title = self.large_font.get_surf("About Effects Lab", "black")
        self.working_surf.blit(title, (center_object_x_surf(title, self.working_surf), 10))

        # -- Buttons --
        self.interactives["close"] = Button((self.rect.topleft[0] + 10, self.rect.topleft[1] + 10), (9, 10),
                                            "../assets/menus/settings/pages/main/close_button", (0, 0), False)

        y_increment = 20
        y = 40

        # bottom disclaimer
        text = self.small_font.get_surf("Made by Andrew Towell (Copyright 2023 Andrew Towell)")
        self.working_surf.blit(text, (center_object_x_surf(text, self.working_surf), y))

        y += y_increment
        text = self.small_font.get_surf("Based on original idea by DaFluffyPotato")
        self.working_surf.blit(text, (center_object_x_surf(text, self.working_surf), y))
        y += y_increment * 0.5
        text = self.small_font.get_surf("Youtube: https://www.youtube.com/@DaFluffyPotato")
        self.working_surf.blit(text, (center_object_x_surf(text, self.working_surf), y))

        y += y_increment
        text = self.small_font.get_surf("This work is distributed under the MIT licence")
        self.working_surf.blit(text, (center_object_x_surf(text, self.working_surf), y))
        y += y_increment * 0.5
        text = self.small_font.get_surf("(licence in distribution folder)")
        self.working_surf.blit(text, (center_object_x_surf(text, self.working_surf), y))

        y += y_increment
        text = self.small_font.get_surf(f"Version: {version}")
        self.working_surf.blit(text, (center_object_x_surf(text, self.working_surf), y))
        y += y_increment * 0.5
        text = self.small_font.get_surf(f"Inital Release: {release}")
        self.working_surf.blit(text, (center_object_x_surf(text, self.working_surf), y))


    def main_page(self):
        # close if button is pressed
        if self.interactives["close"].get_activated():
            self.close = True

    def reset(self):
        self.close = False

    # returns if settings menu should be up or not
    def update(self, mouse_pos):
        # update page buttons
        for button in self.interactives:
            self.interactives[button].update(mouse_pos)

        self.main_page()

    def draw(self):
        self.surface.blit(self.working_surf, self.rect.topleft)

        for button in self.interactives:
            self.interactives[button].draw(self.surface)
