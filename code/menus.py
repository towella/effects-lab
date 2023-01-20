import pygame
from game_data import controls, fonts
from support import resource_path, import_folder, center_object_x_surf
from text import Font
from interactives import *


class Drag_Menu(pygame.sprite.Sprite):
    def __init__(self, path, surface, drag_rect, menu_pos):
        super().__init__()
        resources = import_folder(resource_path(path))
        self.surface = surface
        self.img = resources["background"]
        self.rect = self.img.get_rect()
        self.rect.topleft = menu_pos
        self.drag_button = Button(drag_rect.topleft, (drag_rect.width, drag_rect.height), path + "/drag_button", False, False, False)
        self.button_down = False

        # font
        self.small_font = Font(resource_path(fonts['small_font']), 'black')
        self.large_font = Font(resource_path(fonts['large_font']), 'white')

        # Setup menu text on image
        title = self.large_font.get_surf("Controls", "black")
        self.img.blit(title, (center_object_x_surf(title, self.img), 15))

        x = 10  # starting padding
        y = 40  # starting padding
        rows = 6
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
