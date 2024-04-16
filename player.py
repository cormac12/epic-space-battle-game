import math
import pygame


class Player:
    def __init__(self):
        self.angle = 0
        self.original_image = pygame.image.load("spaceship.png")
        self.display_image = pygame.transform.rotate(self.original_image, self.angle)
        self.display_image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = pygame.Rect(750 - self.display_image.get_width()/2,
                                500 - self.display_image.get_height()/2,
                                self.display_image.get_width(),
                                self.display_image.get_height())
        self.x = 750
        self.y = 500
        self.vx = 0
        self.vy = 0

    def rotate(self, direction):
        if direction == "clockwise":
            self.angle -= 3

        elif direction == "counterclockwise":
            self.angle += 3

        self.angle %= 360
        self.display_image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = pygame.Rect(750 - self.display_image.get_width()/2,
                                500 - self.display_image.get_height()/2,
                                self.display_image.get_width(),
                                self.display_image.get_height())

    def accelerate(self):
        self.vy -= math.cos(math.radians(self.angle)) * .1
        self.vx -= math.sin(math.radians(self.angle)) * .1

    def update_pos(self):
        self.x += self.vx
        self.y += self.vy

