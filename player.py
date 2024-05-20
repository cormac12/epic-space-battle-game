import math
import pygame
from bullet import Bullet
import globals


class Player:
    def __init__(self):
        self.angle = 0



        self.images = {"engine off": pygame.image.load("spaceship off.png"), "engine on": pygame.image.load(
            "spaceship.png")}
        self.image_index = "engine off"
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.rect = pygame.Rect(750 - self.display_image.get_width()/2,
                                500 - self.display_image.get_height()/2,
                                self.display_image.get_width(),
                                self.display_image.get_height())
        self.mask = pygame.mask.from_surface(self.display_image)

        self.x = 750
        self.y = 500
        self.vx = 0
        self.vy = 0

        self.health = 10

        self.engine_on = False
        self.main_engine_str = .06

        self.current_weapon = 0
        self.weapon_names = ["Laser", "Point Defense"]

        self.live_rounds = []
        self.fire_rate = 1 # frames per round

    def rotate(self, direction, magnitude):
        if direction == "clockwise":
            self.angle -= magnitude

        elif direction == "counterclockwise":
            self.angle += magnitude

        self.angle %= 360
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.rect = pygame.Rect(750 - self.display_image.get_width()/2,
                                500 - self.display_image.get_height()/2,
                                self.display_image.get_width(),
                                self.display_image.get_height())

    def accelerate(self):
        self.vy -= math.cos(math.radians(self.angle)) * self.main_engine_str
        self.vx -= math.sin(math.radians(self.angle)) * self.main_engine_str

    def start_engine(self):
        self.engine_on = True
        self.image_index = "engine on"
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)

    def stop_engine(self):
        self.engine_on = False
        self.image_index = "engine off"
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)

    def fire_point_defense(self, angle):
        globals.globals_dict["bullets"].append(Bullet(self.x, self.y, self.vx - 8 * math.sin(math.radians(angle)),
                                               self.vy - 8 * math.cos(math.radians(angle)), -1))
    def update(self):
        if self.engine_on:
            self.accelerate()
        self.x += self.vx
        self.y += self.vy
        self.mask = pygame.mask.from_surface(self.display_image)


