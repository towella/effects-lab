import pygame
from support import import_folder, outline_image, resource_path
from text import Font


# TODO add text
class Button:
    # images must be named 'default', 'hover', 'down' if relevant
    # MUST HAVE DEFAULT
    # TODO add sound
    def __init__(self, rect_pos, dimensions, images_folder_path, blit_offset=(0, 0), outline_hover=True, outline_colour='white'):
        self.outline_hover = outline_hover  # outline default image on hover
        self.outline_colour = outline_colour

        self.hitbox = pygame.Rect(rect_pos[0], rect_pos[1], dimensions[0], dimensions[1])  # clickable area (also used for positioning)
        self.blit_offset = blit_offset

        self.mouse = pygame.mouse.get_pos()
        self.clicked = pygame.mouse.get_pressed()[0]
        self.activated = False

        # import images from button folder
        self.images_dict = import_folder(images_folder_path)
        # If not a toggle, act as normal. Otherwise set image to a switch default so it can be reset later in the init proper
        if "true" not in self.images_dict:
            self.image = self.images_dict['default']
        else:
            self.image = self.images_dict["true"]

    def mouse_hover(self):
        if self.hitbox.collidepoint(self.mouse[0], self.mouse[1]):
            # change to hover image if image is available
            if 'hover' in list(self.images_dict):
                self.image = self.images_dict['hover']
            elif self.outline_hover:
                self.image = outline_image(self.images_dict['default'], self.outline_colour)
                # offset to account for added outline
                self.blit_offset[0] -= 1
                self.blit_offset[1] -= 1
        else:
            self.image = self.images_dict['default']

    def mouse_click(self):
        just_click = pygame.mouse.get_pressed()[0]  # produces three tuple: (b1, b2, b3). Norm click is b1
        # mouse down changes button image to down image if image is avaliable
        if self.hitbox.collidepoint(self.mouse[0], self.mouse[1]) and self.clicked and just_click and 'down' in self.images_dict:
            self.image = self.images_dict['down']
            self.blit_offset = [0, 0]  # prevents hover offset from being applied
        # mouse up after mouse down over button activates button
        elif self.hitbox.collidepoint(self.mouse[0], self.mouse[1]) and self.clicked and not just_click:
            self.activated = True
        else:
            self.activated = False

    def get_activated(self):
        return self.activated

    def get_hover(self, mouse_pos):
        if self.hitbox.collidepoint(mouse_pos[0], mouse_pos[1]):
            return True
        else:
            return False

    def update(self, mouse_pos):
        self.blit_offset = [0, 0]
        self.mouse = mouse_pos
        self.mouse_hover()
        self.mouse_click()
        self.clicked = pygame.mouse.get_pressed()[0]

    def draw(self, surface):
        surface.blit(self.image, (self.hitbox.topleft[0] + self.blit_offset[0], self.hitbox.topleft[1] + self.blit_offset[1]))
        # pygame.draw.rect(surface, 'red', self.hitbox, 1)  #  <-- debug rect


# hover images must be 'hover true' and 'hover false'
class Toggle(Button):
    def __init__(self, toggle, rect_pos, dimensions, images_folder_path, image_offset=(0, 0), outline_hover=True):
        super().__init__(rect_pos, dimensions, images_folder_path, image_offset, outline_hover)
        self.toggle = toggle  # handles state of toggle
        if not self.toggle:
            self.image = self.images_dict["false"]

    def mouse_hover(self):
        if self.hitbox.collidepoint(self.mouse[0], self.mouse[1]):
            if "hover true" in self.images_dict and "hover false" in self.images_dict:
                if self.toggle:
                    self.image = self.images_dict['hover true']
                else:
                    self.image = self.images_dict['hover false']
            elif self.outline_hover:
                # TODO handle offset from border
                if not self.toggle:
                    self.image = outline_image(self.images_dict['false'])
                else:
                    self.image = outline_image(self.images_dict['true'])
                # offset to account for added outline
                self.blit_offset[0] -= 1
                self.blit_offset[1] -= 1
        else:
            if self.toggle:
                self.image = self.images_dict['true']
            else:
                self.image = self.images_dict['false']

    def mouse_click(self):
        just_click = pygame.mouse.get_pressed()[0]  # produces three tuple: (b1, b2, b3). Norm click is b1
        # mouse down changes button image to down image
        if self.hitbox.collidepoint(self.mouse[0], self.mouse[1]) and self.clicked and just_click and "down" in self.images_dict:
            self.image = self.images_dict['down']
            self.blit_offset = [0, 0]  # prevents hover offset from being applied
        if self.hitbox.collidepoint(self.mouse[0], self.mouse[1]) and not self.clicked and just_click:
            self.toggle = not self.toggle
            self.activated = True
        else:
            self.activated = False

    def get_toggle(self):
        return self.toggle

    def set_toggle(self, state):
        self.toggle = bool(state)


class Slider:
    # naming images: 'bar', 'default slider', 'hover slider', 'down slider'
    def __init__(self, bar_pos, bar_dimensions, slide_increment, slider_units, slider_value, slider_y, slider_dimensions,
                 images_folder_path, slider_img_offset=(0, 0), bar_img_offset=(0, 0), outline_hover=True):
        self.activated = False

        # bar length determines range of values on slider (in conjunction with slide_increment)
        self.bar_rect = pygame.Rect(bar_pos[0], bar_pos[1], bar_dimensions[0], bar_dimensions[1])  # bar bounds
        self.slide_increment = slide_increment  # how many pixels per value increase

        x = self.bar_rect.x + self.slide_increment * (slider_value // slider_units)
        self.slider_rect = pygame.Rect(x, slider_y, slider_dimensions[0], slider_dimensions[1])  # slider
        # ensure slider is on bar (value may be beyond range of slider, handle edge cases)
        if self.slider_rect.right > self.bar_rect.right:
            self.slider_rect.centerx = self.bar_rect.right
        elif self.slider_rect.left < self.bar_rect.left:
            self.slider_rect.centerx = self.bar_rect.left

        self.value = slider_value
        self.slider_units = slider_units

        self.slider_offset = slider_img_offset
        self.bar_offset = bar_img_offset
        self.blit_offset = [0, 0]

        self.outline_hover = outline_hover

        self.clicked = pygame.mouse.get_pressed()[0]

        self.images_dict = import_folder(images_folder_path)
        self.image = self.images_dict['default slider']

    def get_value(self):
        return self.value

    def mouse_hover(self, mouse_pos):
        if self.slider_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            if 'hover slider' in self.images_dict:
                self.image = self.images_dict['hover slider']
            elif self.outline_hover:
                self.image = outline_image(self.images_dict['default slider'])
                # offset to account for added outline
                self.blit_offset[0] -= 1
                self.blit_offset[1] -= 1
        else:
            self.image = self.images_dict['default slider']

    def mouse_click(self, mouse_pos):
        just_click = pygame.mouse.get_pressed()[0]  # produces three tuple: (b1, b2, b3). Norm click is b1
        # mouse down changes button image to down image
        if self.bar_rect.collidepoint(mouse_pos[0], mouse_pos[1]) and self.clicked and "down slider" in self.images_dict:
            self.activated = True
            self.image = self.images_dict['down slider']
            # move slider to mouse x if multiple of move increment
            if (mouse_pos[0] - self.bar_rect.left) % self.slide_increment == 0:
                self.slider_rect.centerx = mouse_pos[0]
            # update value
            self.value = (self.slider_rect.centerx - self.bar_rect.left) // self.slide_increment * self.slider_units

            self.blit_offset = [0, 0]  # prevents hover offset from being applied
        else:
            self.activated = False

    def get_activated(self):
        return self.activated

    def update(self, mouse_pos):
        self.blit_offset = [0, 0]
        self.mouse_hover(mouse_pos)
        self.mouse_click(mouse_pos)
        self.clicked = pygame.mouse.get_pressed()[0]

    def draw(self, surface):
        # bar
        surface.blit(self.images_dict['bar'], (self.bar_rect.topleft[0] + self.bar_offset[0], self.bar_rect.topleft[1] + self.bar_offset[1]))
        # slider
        surface.blit(self.image, (self.slider_rect.x + self.slider_offset[0] + self.blit_offset[0],
                                  self.slider_rect.y + self.slider_offset[1] + self.blit_offset[1]))

        #pygame.draw.rect(surface, 'red', self.slider_rect, 1)  #< - test
        #pygame.draw.rect(surface, 'red', self.bar_rect, 1)  #<-- test


# source page https://stackoverflow.com/questions/46390231/how-can-i-create-a-text-input-box-with-pygame
class InputBox:
    def __init__(self, x, y, w, h, inactive_colour, active_colour, max_chars, font_path, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.colours = {'inactive': inactive_colour, 'active': active_colour}
        self.colour = inactive_colour
        self.default_text = text
        self.text = text
        # maximum characters allowed for text box
        if max_chars < len(text):
            self.max_chars = len(text)
        else:
            self.max_chars = max_chars
        self.active = False
        self.font = Font(font_path, self.colours['inactive'])

    def handle_event(self, events):
        if pygame.mouse.get_pressed()[0]:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                # Toggle the active variable and clear text if the text is still the default text. Otherwise keep it
                self.active = True
                if self.text == self.default_text:
                    self.text = ''
            else:
                self.active = False

        # TODO fix up events vs key_down
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        self.active = False
                    # LMETA is command button
                    # TODO fix
                    elif event.key == pygame.K_LMETA:
                        self.text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode  # adds char string to text
                    # Re-render the text.
        # length cap
        if len(self.text) > self.max_chars:
            self.text = self.text[:self.max_chars]

    def update(self, events):
        self.handle_event(events)
        # Change the current color of the input box.
        self.colour = self.colours['active'] if self.active else self.colours['inactive']
        # Resize the box if the text is too long.
        self.rect.w = max(200, self.font.width(self.text) + 2)

    def draw(self, screen):
        # Blit the text.
        self.font.render(self.text, screen, (self.rect.x+2, self.rect.y+2))
        # Blit the rect.
        pygame.draw.rect(screen, self.colour, self.rect, 1)

