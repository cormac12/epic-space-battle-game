import pygame
import globals
import math


class Enemy:
    def __init__(self, x, y, vx, vy):
        self.angle = 0

        self.my_font = pygame.font.SysFont('Arial', 15)

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
        self.vy -= math.cos(math.radians(self.angle)) * 0.2
        self.vx -= math.sin(math.radians(self.angle)) * 0.2

    def update_pos(self):
        self.x += self.vx
        self.y += self.vy

    def get_angle_to_player(self, player_x, player_y):
        if self.x > player_x and self.y > player_y:
            return math.degrees(math.atan((self.x - player_x)/(self.y-player_y)))
        elif self.x > player_x and self.y < player_y:
            return math.degrees((math.atan((self.x - player_x)/(self.y-player_y)))) + 180
        elif self.x < player_x and self.y < player_y:
            return math.degrees((math.atan((self.x - player_x)/(self.y-player_y)))) + 180
        elif self.x < player_x and self.y > player_y:
            return math.degrees(math.atan((self.x - player_x)/(self.y-player_y)))
        else:
            return 0

    def point(self, direction):
        self.angle = direction
        self.angle %= 360
        self.display_image = pygame.transform.rotate(self.original_image, self.angle)

    def target_direction(self, target): # rotates the ship toward the player.
        # returns true when pointing at the target
        if -5 < self.angle - target < 5:
            self.point(target)
            self.cw = self.my_font.render(str((self.angle - target) % 360), True, (255, 255, 255))
            self.ccw = self.my_font.render(str((self.angle + target) % 360), True, (255, 255, 255))
            return True
        elif (self.angle - target) % 360 <= (self.angle + target) % 360:
            self.rotate("clockwise")
        elif (self.angle - target) % 360 >= (self.angle + target) % 360:
            self.rotate("counterclockwise")

        self.cw = self.my_font.render(str((self.angle - target) % 360), True, (255, 255, 255))
        self.ccw = self.my_font.render(str((self.angle + target) % 360), True, (255,255,255))
        return False

    def target_vector(self, direction, magnitude, player_vx, player_vy):
        # rotates and accelerates craft in order to achieve target relative velocity vector to player
        target_vx = magnitude * math.sin(math.radians(direction))
        target_vy = magnitude * math.cos(math.radians(direction))

        if self.vx - player_vx != target_vx and self.vy - player_vy != target_vy:

            if self.vx > player_vx and self.vy > player_vy:
                target_angle = math.degrees(math.atan((self.vx - player_vx)/(self.vy-player_vy)))
            elif self.vx > player_vx and self.vy < player_vy:
                target_angle = math.degrees((math.atan((self.vx - player_vx)/(self.vy-player_vy)))) + 180
            elif self.vx < player_vx and self.vy < player_vy:
                target_angle = math.degrees((math.atan((self.vx - player_vx)/(self.vy-player_vy)))) + 180
            elif self.vx < player_vx and self.vy > player_vy:
                target_angle = math.degrees(math.atan((self.vx - player_vx)/(self.vy-player_vy)))
            else:
                target_angle = 0

            # self.target_direction(target_angle)
            if (self.target_direction(target_angle) and
                    round(math.sqrt((self.vx-player_vx)**2 + (self.vy-player_vy)**2),0) != round(math.sqrt(target_vx**2 + target_vy**2),0)):
                self.accelerate()
                print("Acc")



