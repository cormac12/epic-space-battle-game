import pygame
from player import Player
import globals
from enemy import Enemy
import random
import time
import math


def get_angle_to_point(x1,y1, x2, y2):
    if y1 - y2 != 0:
        if x1 >= x2 and y1 >= y2:
            return math.degrees(math.atan((x1 - x2) / (y1 - y2)))
        elif x1 >= x2 and y1 <= y2:
            return math.degrees((math.atan((x1 - x2) / (y1 - y2)))) + 180
        elif x1 <= x2 and y1 <= y2:
            return math.degrees((math.atan((x1 - x2) / (y1 - y2)))) + 180
        elif x1 <= x2 and y1 >= y2:
            return math.degrees(math.atan((x1 - x2) / (y1 - y2)))
    elif x1 - x2 < 0:
        return 270
    else:
        return 90


# set up pygame modules
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Arial', 15)
pygame.display.set_caption("Space Fight!")

# set up variables for the display
size = (1500, 1000)
screen = pygame.display.set_mode(size)


# I'm just keeping this as a placeholder for when I need to add text
name = "Mr. Das"

# render the text for later
display_name = my_font.render(name, True, (255, 255, 255))

# The loop will carry on until the user exits the game (e.g. clicks the close button).
run = True

p = Player()

camera_pos = (0,0)

globals.globals_dict["player_x"] = p.x
globals.globals_dict["player_y"] = p.y
globals.globals_dict["camera_pos"] = camera_pos

enemies = [Enemy(100, 100, 2, 2)]

laser_image = pygame.image.load("laser.png")

target_fps = 45
frame = 0
clock = pygame.time.Clock()
time_1 = 0
time_2 = 0
fps_list = []
laser_on = False
last_p_angle = ""

# -------- Main Program Loop -----------
while run:
    clock.tick(target_fps)

    frame += 1

    time_1 = time_2
    time_2 = time.time()

    if time_2 - time_1 != 0:
        real_fps = 1/(time_2 - time_1)
    else:
        real_fps = 0
    fps_list.append(real_fps)
    if len(fps_list) > 100:
        fps_list.pop(0)




    mouse_pos = pygame.mouse.get_pos()

    # ------ Update Globals -------
    globals.globals_dict["player_x"] = p.x
    globals.globals_dict["player_y"] = p.y
    globals.globals_dict["camera_pos"] = camera_pos
    globals.globals_dict["mouse_pos"] = mouse_pos

    # ------ End of Update Globals --------

    # ------ Update World Objects ---------
    p.update_coords()
    camera_pos = (p.x - 750, p.y - 500)

    for i in enemies:
        if i.alive:
            if i.get_distance_to_player() > 300:
                i.target_vector(i.get_angle_to_player(p.x, p.y), 2, p.vx, p.vy)
            elif i.get_distance_to_player() < 150:
                i.target_vector(i.get_angle_to_player(p.x, p.y) + 180, 1, p.vx, p.vy)
            else:
                i.target_vector(i.get_angle_to_player(p.x, p.y) + 90, 5.5, p.vx, p.vy)
            i.update_coords()
        else:
            enemies.remove(i)

    for i in p.live_rounds:
        i.update_coords()



    keys = pygame.key.get_pressed()

    if keys[pygame.K_d]:
        p.rotate("clockwise",1.5)
    elif keys[pygame.K_e]:
        p.rotate("clockwise", .5)
    if keys[pygame.K_a]:
        p.rotate("counterclockwise", 1.5)
    elif keys[pygame.K_q]:
        p.rotate("counterclockwise", .5)
    if keys[pygame.K_w]:
        p.accelerate()
    if keys[pygame.K_SPACE]:
        fps = 1
    if keys[pygame.K_UP]:
        target_fps *= 1.1
    if keys[pygame.K_DOWN]:
        target_fps /= 1.1

    if pygame.mouse.get_pressed()[0]:
        if p.current_weapon == 0:
            laser_on = True
            if p.angle != last_p_angle:
                laser_image_transformed = pygame.transform.rotate(laser_image, p.angle)
                laser_mask = pygame.mask.from_surface(laser_image_transformed)
                if p.angle <= 90:
                    laser_rect = pygame.Rect(750-laser_image_transformed.get_width() + 2.5 * math.cos(math.radians(p.angle)),
                                             500-laser_image_transformed.get_height() + 2.5 * math.sin(math.radians(p.angle)),
                                             laser_image_transformed.get_width(),
                                             laser_image_transformed.get_height())
                elif p.angle <= 180:
                    laser_rect = pygame.Rect(750-laser_image_transformed.get_width() - 2.5 * math.cos(math.radians(p.angle)),
                                             500 - 2.5 * math.sin(math.radians(p.angle)),
                                             laser_image_transformed.get_width(),
                                             laser_image_transformed.get_height())
                elif p.angle <= 270:
                    laser_rect = pygame.Rect(750 + 2.5 * math.cos(math.radians(p.angle)),
                                             500 + 2.5 * math.sin(math.radians(p.angle)),
                                             laser_image_transformed.get_width(),
                                             laser_image_transformed.get_height())
                elif p.angle <= 360:
                    laser_rect = pygame.Rect(750 - 2.5 * math.cos(math.radians(p.angle)) ,
                                             500-laser_image_transformed.get_height() - 2.5 * math.sin(math.radians(p.angle)),
                                             laser_image_transformed.get_width(),
                                             laser_image_transformed.get_height())
            last_p_angle = p.angle
        elif p.current_weapon == 1:
            if frame % p.fire_rate == 0:
                p.fire_point_defense(get_angle_to_point(750,500,mouse_pos[0],mouse_pos[1])
                                     + random.randint(-10,10)/10)


    else:
        laser_on = False

    # If there are more than a thousand projectiles in the world, the oldest will be deleted
    # 
    while len(p.live_rounds) > 1000:
        p.live_rounds.pop(0)

    # --- Main event loop
    for event in pygame.event.get():  # User did something
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                p.start_engine()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                p.stop_engine()
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0 and p.current_weapon < len(p.weapon_names)-1:
                p.current_weapon += 1
            elif event.y < 0 and p.current_weapon > 0:
                p.current_weapon -= 1
        elif event.type == pygame.QUIT:  # If user clicked close
            run = False



    if len(enemies) == 0:
        enemies.append(Enemy(random.randint(round(camera_pos[0]), round(camera_pos[0]+1200)),
                             random.randint(round(camera_pos[1]), round(camera_pos[1]+800)),
                             (p.vx + random.randint(-20, 20)/10), (p.vy + random.randint(-20, 20)/10)))

    for i in enemies:
        for b in p.live_rounds:
            if i.alive and i.mask.overlap(pygame.Mask((2,2),True), (b.x - camera_pos[0] - i.rect.left, b.y - camera_pos[1] - i.rect.top)):
                i.health -= 2
                p.live_rounds.remove(b)


    display_x = my_font.render(str(enemies[0].vx), True, (255,255,255))
    display_y = my_font.render(str(enemies[0].vy), True, (255,255,255))

    # display_x = my_font.render(str(enemies[0].cw), True, (255,255,255))
    # display_y = my_font.render(str(enemies[0].ccw), True, (255,255,255))
    display_fps = my_font.render(str(round(sum(fps_list)/len(fps_list))) + "/" + str(target_fps), True, (255,255,255))
    screen.fill((0, 0, 0))
    # ------Blit Zone Start------

    if laser_on:
        # screen.blit(laser_image_transformed, laser_rect)
        pygame.draw.line(screen, (15,225,15), (750, 500), (750 + -1000 * math.sin(math.radians(p.angle)),
                                                         500 + -1000 *math.cos(math.radians(p.angle))), width=5)
        for i in enemies:
            if i.alive and i.mask.overlap(laser_mask, (laser_rect.left-i.rect.left,laser_rect.top -i.rect.top)):
                i.health -= 1

    for i in p.live_rounds:
        pygame.draw.rect(screen, (255,150,50), pygame.Rect(i.x - camera_pos[0], i.y -camera_pos[1], 2,2))

    screen.blit(p.display_image, p.rect)



    for i in enemies:
        if i.alive:
            screen.blit(i.display_image, i.rect)

    screen.blit(display_x, (0, 0))
    screen.blit(display_y, (0, 15))
    screen.blit(display_fps, (0, size[1]-30))

    # screen.blit(i, (100-p.x, 100-p.y))

    # ------Blit Zone End------

    pygame.display.update()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()


