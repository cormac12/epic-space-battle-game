import math
import pygame


class Player:
    def __init__(self):
        self.angle = 0



        self.images = {"engine off": pygame.image.load("spaceship off.png"), "engine on": pygame.image.load("spaceship.png")}
        self.image_index = "engine off"
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.rect = pygame.Rect(750 - self.display_image.get_width()/2,
                                500 - self.display_image.get_height()/2,
                                self.display_image.get_width(),
                                self.display_image.get_height())
        self.x = 750
        self.y = 500
        self.vx = 0
        self.vy = 0
        self.engine_on = False

    def rotate(self, direction):
        if direction == "clockwise":
            self.angle -= 3

        elif direction == "counterclockwise":
            self.angle += 3

        self.angle %= 360
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.rect = pygame.Rect(750 - self.display_image.get_width()/2,
                                500 - self.display_image.get_height()/2,
                                self.display_image.get_width(),
                                self.display_image.get_height())

    def accelerate(self):
        self.vy -= math.cos(math.radians(self.angle)) * .2
        self.vx -= math.sin(math.radians(self.angle)) * .2

    def start_engine(self):
        self.engine_on = True
        self.image_index = "engine on"
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)

    def stop_engine(self):
        self.engine_on = False
        self.image_index = "engine off"
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)


    def update_coords(self):
        if self.engine_on:
            self.accelerate()
        self.x += self.vx
        self.y += self.vy

