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

        self.start_frame = globals.globals_dict["frame"]

        self.do_targeting = do_targeting  # Boolean. if false, it will fly in a straight line
        self.target = target  # Int. if -1, the target is the player. Otherwise, it is an index in the enemy list
        self.engine_str = 0.4

        self.original_image = pygame.image.load("rocket.png")
        self.parent = parent  # Int. if -1, the target is the player. Otherwise, it is an index in the enemy list
        self.alive = True

        self.exploding = False
        self.explosion_start = 0
        self.explosion_image = pygame.image.load("explosion.png")
        self.explosion_screen_x = 0
        self.explosion_screen_y = 0

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
            # if globals.globals_dict["frame"] <= self.start_frame + 26:
                # I put a limit on torpedo speed to limit times when the torpedo is fast enough to fly through the player
            self.vy -= math.cos(math.radians(self.angle)) * self.engine_str
            self.vx -= math.sin(math.radians(self.angle)) * self.engine_str
        else:
            if (globals.globals_dict["frame"] - self.explosion_start) <= 7:
                if (globals.globals_dict["frame"] - self.explosion_start) <= 5:
                    self.display_image = pygame.transform.smoothscale_by(self.explosion_image,
                                                                        (globals.globals_dict["frame"] - self.explosion_start) /5)
                else:
                    self.display_image = pygame.transform.smoothscale_by(self.explosion_image,
                                                                        (2-(globals.globals_dict["frame"] - self.explosion_start - 5))/2)
                self.rect = pygame.Rect(self.explosion_screen_x - self.display_image.get_width()/2,
                                        self.explosion_screen_y - self.display_image.get_height()/2,
                                        self.display_image.get_width(), self.display_image.get_height())

            else:
                self.alive = False

            self.mask = pygame.mask.from_surface(self.display_image)


    def explode(self):
        if not self.exploding:
            self.exploding = True
            self.explosion_start = globals.globals_dict["frame"]
            self.explosion_screen_x = self.x - globals.globals_dict["camera_pos"][0]
            self.explosion_screen_y = self.y - globals.globals_dict["camera_pos"][1]
            self.mask = pygame.mask.from_surface(self.display_image)







