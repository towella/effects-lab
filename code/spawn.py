import pygame


class Spawn(pygame.sprite.Sprite):
    def __init__(self, x, y, name, player_facing):
        super().__init__()
        self.x = x
        self.y = y
        self.name = name
        self.player_facing = player_facing

    def update(self, scroll_value):
        pass