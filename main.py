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

enemies = [ Enemy(100, 100, 0, 0)]

fps = 30

clock = pygame.time.Clock()

# -------- Main Program Loop -----------
while run:

    clock.tick(fps)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_d]:
        p.rotate("clockwise")
    if keys[pygame.K_a]:
        p.rotate("counterclockwise")
    if keys[pygame.K_w]:
        p.accelerate()
    if keys[pygame.K_SPACE]:
        fps = 1
    if keys[pygame.K_UP]:
        fps *= 1.5
    if keys[pygame.K_DOWN]:
        fps /= 1.5


    p.update_coords()
    # camera_pos = (p.x + p.rect.width/2 - 750, p.y + p.rect.height/2 - 500)
    camera_pos = (p.x - 750, p.y - 500)

    for i in enemies:
        if random.randint(1,1) == 1:
            # i.rotate("clockwise")
            # i.accelerate()
            # i.target_direction(i.get_angle_to_player(p.x, p.y))
            i.target_vector(0, 1, p.vx, p.vy)

    for i in enemies:
        i.update_coords()

    # --- Main event loop
    for event in pygame.event.get():  # User did something
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                p.start_engine()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                p.stop_engine()
        if event.type == pygame.QUIT:  # If user clicked close
            run = False

    # display_x = my_font.render(str(camera_pos[0]), True, (255,255,255))
    # display_y = my_font.render(str(camera_pos[1]), True, (255,255,255))

    # display_x = my_font.render(str(enemies[0].cw), True, (255,255,255))
    # display_y = my_font.render(str(enemies[0].ccw), True, (255,255,255))
    display_fps = my_font.render(str(fps), True, (255,255,255))
    screen.fill((0, 0, 0))
    # ------Blit Zone Start------

    screen.blit(p.display_image, p.rect)

    for i in enemies:
        screen.blit(i.display_image, pygame.Rect(i.x - camera_pos[0] - i.display_image.get_width()/2,
                                                 i.y - camera_pos[1] - i.display_image.get_height()/2, i.display_image.get_width(),
                                                 i.display_image.get_height()))
    # screen.blit(enemies[0].cw, (0, 0))
    # screen.blit(enemies[0].ccw, (0, 15))
    screen.blit(display_fps, (0, size[1]-30))
    # screen.blit(i, (100-p.x, 100-p.y))

    print("fix line 97 of enemy.py")

    # ------Blit Zone End------

    pygame.display.update()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()


