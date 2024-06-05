import pygame
import globals
import math
from laser import Laser



class Enemy:
    def __init__(self, x, y, vx, vy, type, index):
        self.type = type  # type 0 is a basic fighter type 1 is a gunship
        self.angle = 0
        self.index = index





        self.engine_on = False


        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True

        if self.type == 0:
            self.images = {"engine off": pygame.image.load("spaceship2 off.png"), "engine on": pygame.image.load(
                "spaceship2.png")}
            self.image_index = "engine off"

            self.health = 50
            self.main_engine_str = 0.25
            self.turn_rate = 8

            self.ai_mode = 0
        elif self.type == 1:
            # TEMPORARY IMAGE CODE
            self.images = {"engine off": pygame.image.load("gunship 00.png"), "engine on": pygame.image.load(
                "gunship 11.png")}
            self.image_index = "engine off"

            self.health = 1000
            self.main_engine_str = .05
            self.turn_rate = 1

            self.ai_mode = 2
            self.laser_index = len(globals.globals_dict["lasers"])
            globals.globals_dict["lasers"].append(Laser((self.x, self.y), self.angle, 5,  (255, 10, 255), 10, self.index))

            self.last_laser_time = 0
            self.sweep_direction = 0
            self.start_angle = 0
            self.laser_is_charging = False
            self.laser_is_on = False


        self.torpedo_cool_down_start = globals.globals_dict["frame"]  # Records the frame when the last torpedo was fired
        self.torpedo_cool_down_duration = 60  # How long the wait is before another torpedo can be fired.


        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.mask = pygame.mask.from_surface(self.display_image)
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0] - self.display_image.get_width() / 2,
                    self.y - globals.globals_dict["camera_pos"][1] - self.display_image.get_height() / 2,
                    self.display_image.get_width(),
                    self.display_image.get_height())

    def rotate(self, direction):
        if direction == "clockwise":
            self.angle -= self.turn_rate

        elif direction == "counterclockwise":
            self.angle += self.turn_rate


        self.angle %= 360
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0] - self.display_image.get_width() / 2,
                    self.y - globals.globals_dict["camera_pos"][1] - self.display_image.get_height() / 2, self.display_image.get_width(),
                    self.display_image.get_height())
        self.mask = pygame.mask.from_surface(self.display_image)


    def start_engine(self):
        self.engine_on = True
        self.image_index = "engine on"
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0] - self.display_image.get_width() / 2,
                    self.y - globals.globals_dict["camera_pos"][1] - self.display_image.get_height() / 2, self.display_image.get_width(),
                    self.display_image.get_height())
        self.mask = pygame.mask.from_surface(self.display_image)



    def stop_engine(self):
        self.engine_on = False
        self.image_index = "engine off"
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0] - self.display_image.get_width() / 2,
                    self.y - globals.globals_dict["camera_pos"][1] - self.display_image.get_height() / 2, self.display_image.get_width(),
                    self.display_image.get_height())
        self.mask = pygame.mask.from_surface(self.display_image)

    def accelerate(self):
        self.vy -= math.cos(math.radians(self.angle)) * self.main_engine_str
        self.vx -= math.sin(math.radians(self.angle)) * self.main_engine_str

    def update(self):
        if self.engine_on:
            self.accelerate()
        self.x += self.vx
        self.y += self.vy
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0] - self.display_image.get_width() / 2,
                    self.y - globals.globals_dict["camera_pos"][1] - self.display_image.get_height() / 2, self.display_image.get_width(),
                    self.display_image.get_height())
        if self.health <= 0:
            self.alive = False

    def get_angle_to_player(self):
        if self.y-globals.globals_dict["player_y"] != 0:
            if self.x >= globals.globals_dict["player_x"] and self.y >= globals.globals_dict["player_y"]:
                return math.degrees(math.atan((self.x - globals.globals_dict["player_x"])/(self.y-globals.globals_dict["player_y"])))
            elif self.x >= globals.globals_dict["player_x"] and self.y <= globals.globals_dict["player_y"]:
                return math.degrees((math.atan((self.x - globals.globals_dict["player_x"])/(self.y-globals.globals_dict["player_y"])))) + 180
            elif self.x <= globals.globals_dict["player_x"] and self.y <= globals.globals_dict["player_y"]:
                return math.degrees((math.atan((self.x - globals.globals_dict["player_x"])/(self.y-globals.globals_dict["player_y"])))) + 180
            elif self.x <= globals.globals_dict["player_x"] and self.y >= globals.globals_dict["player_y"]:
                return math.degrees(math.atan((self.x - globals.globals_dict["player_x"])/(self.y-globals.globals_dict["player_y"])))
        elif self.x <= globals.globals_dict["player_x"]:
            return 270
        else:
            return 90



    def get_distance_to_player(self):
        return math.sqrt((globals.globals_dict["player_x"] - self.x)**2 + (globals.globals_dict["player_y"] - self.y)**2)

    def point(self, direction):
        self.angle = direction
        self.angle %= 360
        self.display_image = pygame.transform.rotate(self.images[self.image_index], self.angle)
        self.mask = pygame.mask.from_surface(self.display_image)
        self.rect = pygame.Rect(self.x - globals.globals_dict["camera_pos"][0] - self.display_image.get_width() / 2,
                    self.y - globals.globals_dict["camera_pos"][1] - self.display_image.get_height() / 2, self.display_image.get_width(),
                    self.display_image.get_height())

    def target_direction(self, target): # rotates the ship toward the player.
        # returns true when pointing at the target
        target %= 360
        target = round(target, 0)

        if self.angle < 180:
            if self.angle <= (target + self.turn_rate) % 360 and (self.angle + self.turn_rate) % 360 >= target:
                self.point(target)

                return True
            elif self.angle < target <= self.angle + 180:
                self.rotate("counterclockwise")
            elif self.angle > target or self.angle + 180 < target:
                self.rotate("clockwise")
        elif self.angle > 180:

            if ((self.angle <= (target + self.turn_rate) % 360 or self.angle <= target + self.turn_rate)
                    and (target <= (self.angle + self.turn_rate) % 360 or target <= self.angle + self.turn_rate)):
                self.point(target)

                return True
            elif self.angle - 180 <= target < self.angle:
                self.rotate("clockwise")
            elif target > self.angle or target < self.angle - 180:
                self.rotate("counterclockwise")
        elif self.angle == 180:
            if 175 <= target <= 185:
                self.point(target)
                return True
            elif target < self.angle:
                self.rotate("clockwise")
            else:
                self.rotate("counterclockwise")


        return False






    def target_vector(self, direction, magnitude, player_vx, player_vy):
        # rotates and accelerates craft in order to achieve target relative velocity vector to player
        target_vx = magnitude * math.sin(math.radians(direction))*-1
        target_vy = magnitude * math.cos(math.radians(direction))*-1


        deviation_x = target_vx + (player_vx - self.vx)
        deviation_y = target_vy + (player_vy - self.vy)



        if deviation_y != 0:
            if deviation_x <= 0 and deviation_y <= 0:
                deviation_angle = math.degrees(math.atan(deviation_x/deviation_y))
            elif deviation_x <= 0 and deviation_y >= 0:
                deviation_angle = math.degrees((math.atan(deviation_x/deviation_y))) + 180
            elif deviation_x >= 0 and deviation_y >= 0:
                deviation_angle = math.degrees((math.atan(deviation_x/deviation_y))) + 180
            elif deviation_x >= 0 and deviation_y <= 0:
                deviation_angle = math.degrees(math.atan(deviation_x/deviation_y)) + 360
            else:
                deviation_angle = 1
        elif deviation_x < 0:
            deviation_angle = 270
        else:
            deviation_angle = 90


        deviation_magnitude = math.sqrt(deviation_x**2 + deviation_y**2)

        # self.target_direction(deviation_angle)
        if deviation_x != 0 or deviation_y != 0:
            on_target = self.target_direction(deviation_angle)
            if on_target and deviation_magnitude <= self.main_engine_str:
                self.vx = (player_vx + target_vx)
                self.vy = (player_vy + target_vy)

                # print("X", self.vx)
                # print("Y", self.vy)
            elif on_target:
                self.start_engine()
            else:
                self.stop_engine()




