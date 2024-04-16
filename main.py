import pygame
from player import Player
import globals
from enemy import Enemy
import random

# set up pygame modules
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Arial', 15)
pygame.display.set_caption("Space Fight!")

# set up variables for the display
size = (1500, 1000)
screen = pygame.display.set_mode(size)

name = "Mr. Das"

# render the text for later
display_name = my_font.render(name, True, (255, 255, 255))

# The loop will carry on until the user exits the game (e.g. clicks the close button).
run = True

p = Player()

camera_pos = (0,0)

globals.globals_dict["player_x"] = p.x
globals.globals_dict["player_y"] = p.y

enemies = [Enemy(750, 500, 0, 0), Enemy(850, 550, 0, 0)]

clock = pygame.time.Clock()

# -------- Main Program Loop -----------
while run:

    clock.tick(30)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_d]:
        p.rotate("clockwise")
    if keys[pygame.K_a]:
        p.rotate("counterclockwise")
    if keys[pygame.K_w]:
        p.accelerate()

    p.update_pos()

    for i in enemies:
        if random.randint(1,1) == 1:
            i.rotate("clockwise")
            i.accelerate()

    for i in enemies:
        i.update_pos()


    globals.globals_dict["player_x"] = p.x
    globals.globals_dict["player_y"] = p.y

    # e.rect = pygame.Rect(e.x - globals.globals_dict["player_x"], e.y - globals.globals_dict["player_y"],
    #                         e.display_image.get_width(), e.display_image.get_height())

    # --- Main event loop
    for event in pygame.event.get():  # User did something
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                print("Add in sprite change pls")
        if event.type == pygame.QUIT:  # If user clicked close
            run = False

    display_x = my_font.render(str(p.x), True, (255,255,255))
    display_y = my_font.render(str(p.y), True, (255,255,255))

    screen.fill((0, 0, 0))
    # ------Blit Zone Start------

    screen.blit(p.display_image, p.rect)

    for i in enemies:
        screen.blit(i.display_image, pygame.Rect(i.x - p.x - i.display_image.get_width()/2,
                                                 i.y - p.y - i.display_image.get_height()/2, i.display_image.get_width(),
                                                 i.display_image.get_height()))
    screen.blit(display_x, (0, 0))
    screen.blit(display_y, (0, 15))
    # screen.blit(i, (100-p.x, 100-p.y))

    # ------Blit Zone End------

    pygame.display.update()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()


