import pygame


class Trigger(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name):
        super().__init__()
        self.hitbox = pygame.Rect(x, y, width, height)
        self.name = name

    def update(self, scroll_value):
        pass