import pygame
import math
import globals
from bullet import Bullet


class Torpedo:
    def __init__(self, x,y,vx,vy,angle, do_targeting, target, parent):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.angle = angle

        self.do_targeting = do_targeting  # Boolean. if false, it will fly in a straight line
        self.target = target  # Int. if -1, the target is the player. Otherwise, it is an index in the enemy list
        self.engine_str = 0.75

        self.original_image = pygame.image.load("rocket.png")
        self.parent = parent
        self.alive = True
        self.exploding = False
        self.explosion_start = 0

        if self.target == -1:
            self.display_image = pygame.transform.rotate(self.original_image, angle)

        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0], self.y - globals.globals_dict["camera_pos"][1],
                                self.display_image.get_width(),self.display_image.get_height())

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0] - self.display_image.get_width()/2,
                                self.y - globals.globals_dict["camera_pos"][1] - self.display_image.get_height()/2,
                                self.display_image.get_width(),self.display_image.get_height())

        if not self.exploding:
            self.vy -= math.cos(math.radians(self.angle)) * self.engine_str
            self.vx -= math.sin(math.radians(self.angle)) * self.engine_str






    def explode(self):
        for i in range(100):
            angle = 360/(i+1)
            globals.globals_dict["bullets"].append(Bullet(self.x,self.y,
                                                          self.vx - math.cos(angle),
                                                          self.vy - math.sin(angle), 0))
        self.alive = False






