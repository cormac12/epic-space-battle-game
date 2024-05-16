import pygame
import math
import globals


class Torpedo:
    def __init__(self, x,y,vx,vy,angle, do_targeting, target):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.angle = angle

        self.do_targeting = do_targeting  # Boolean. if false, it will fly in a straight line
        self.target = target  # Int. if -1, the target is the player. Otherwise, it is an index in the enemy list
        self.engine_str = 0.75

        self.original_image = pygame.image.load("rocket.png")

        if self.target == -1:
            self.display_image = pygame.transform.rotate(self.original_image, angle)

        self.rect = self.display_image.get_rect(center= (self.x - globals.globals_dict["camera_pos"][0],self.y - globals.globals_dict["camera_pos"][1]))


    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy -= math.cos(math.radians(self.angle)) * self.engine_str
        self.vx -= math.sin(math.radians(self.angle)) * self.engine_str
        self.rect = self.display_image.get_rect(
            center=(self.x - globals.globals_dict["camera_pos"][0], self.y - globals.globals_dict["camera_pos"][1]))


    def explode(self):
        return None






