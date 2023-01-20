import pygame


class Radial_Blast(pygame.sprite.Sprite):
    def __init__(self, radius, colour, thickness, surface, pos, radius_increment=3, expire=150, double_circle=False):
        super().__init__()
        self.surface = surface
        self.pos = pos

        self.radius = int(radius)
        self.radius_increment = int(radius_increment)  # by how much the radius is increased each update
        self.expire = int(expire)  # radius size when the blast dies
        self.colour = colour
        self.thickness = int(thickness)
        self.double_circle = double_circle
        self.double_circle_colour = 'black'

    def update(self):
        # double circles
        self.thickness -= 0.2
        if self.double_circle:
            if self.thickness <= 2:
                self.thickness = 2
        else:
            if self.thickness <= 1:
                self.thickness = 1

        self.radius += self.radius_increment
        if self.radius > self.expire:
            self.kill()

    def draw(self):
        pygame.draw.circle(self.surface, self.colour, self.pos, self.radius, int(self.thickness))
        if self.double_circle:
            pygame.draw.circle(self.surface, self.double_circle_colour, self.pos, self.radius - 2, 1)
            pygame.draw.circle(self.surface, self.double_circle_colour, self.pos, self.radius, 1)


