import pygame
import globals
import math


class Enemy:
    def __init__(self, x, y, vx, vy):
        self.angle = 0

        self.original_image = pygame.image.load("spaceship2.png")
        self.display_image = pygame.transform.rotate(self.original_image, self.angle)
        self.display_image = pygame.transform.rotate(self.original_image, self.angle)

        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

        self.rect = pygame.Rect(self.x - globals.globals_dict["player_x"], self.y - globals.globals_dict["player_y"],
                                self.display_image.get_width(), self.display_image.get_height())

    def rotate(self, direction):
        if direction == "clockwise":
            self.angle -= 5

        elif direction == "counterclockwise":
            self.angle += 5

        self.angle %= 360
        self.display_image = pygame.transform.rotate(self.original_image, self.angle)

    def accelerate(self):
        self.vy -= math.cos(math.radians(self.angle)) * .1
        self.vx -= math.sin(math.radians(self.angle)) * .1

    def update_pos(self):
        self.x += self.vx
        self.y += self.vy