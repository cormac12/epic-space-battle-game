import pygame
import globals
class Bullet:
    def __init__(self, x, y, vx, vy, size, color, damage, parent):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0], self.y - globals.globals_dict["camera_pos"][1],
                                self.size[0], self.size[1])
        self.color = color
        self.parent = parent
        self.start_frame = globals.globals_dict["frame"]
        self.damage = damage

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0], self.y - globals.globals_dict["camera_pos"][1],
                                self.size[0], self.size[1])
