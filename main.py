import pygame
from player import Player
import globals
from enemy import Enemy
import random
import time
import math
from torpedo import Torpedo


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
globals.globals_dict["frame"] = 0
globals.globals_dict["bullets"] = []

enemies = [Enemy(100, 100, 2, 2)]
torpedoes = []

laser_image = pygame.image.load("laser.png")

target_fps = 30
frame = 0
clock = pygame.time.Clock()
time_1 = 0
time_2 = 0
fps_list = []
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
    p.update()
    camera_pos = (p.x - 750, p.y - 500)
    # ------ Update Globals -------
    globals.globals_dict["player_x"] = p.x
    globals.globals_dict["player_y"] = p.y
    globals.globals_dict["camera_pos"] = camera_pos
    globals.globals_dict["mouse_pos"] = mouse_pos
    globals.globals_dict["frame"] = frame

    # ------ End of Update Globals --------

    # ------ Update World Objects ---------


    for t in torpedoes:
        t.update()
        if not t.exploding and frame > t.start_frame + 150:
            t.explode()
        if not t.alive:
            torpedoes.remove(t)




    i = 0
    for e in enemies:
        if e.alive:
            e.update()
            if e.get_distance_to_player() > 300:
                e.target_vector(e.get_angle_to_player(), 2, p.vx, p.vy)
            elif e.get_distance_to_player() < 150:
                e.target_vector(e.get_angle_to_player() + 180, 2, p.vx, p.vy)
            else:
                e.target_vector(e.get_angle_to_player() + 60, 6, p.vx, p.vy)
            if frame > e.cool_down_start + e.cool_down_duration:
                torpedoes.append(Torpedo(e.x, e.y, e.vx, e.vy, e.get_angle_to_player(), False, -1, i))
                e.cool_down_start = frame

        else:
            enemies.pop(i)
        i += 1



    for i in globals.globals_dict["bullets"]:
        i.update()




    keys = pygame.key.get_pressed()

    if keys[pygame.K_d]:
        p.rotate("clockwise",2.25)
    elif keys[pygame.K_e]:
        p.rotate("clockwise", .75)
    if keys[pygame.K_a]:
        p.rotate("counterclockwise", 2.25)
    elif keys[pygame.K_q]:
        p.rotate("counterclockwise", .75)
    if keys[pygame.K_SPACE]:
        fps = 1
        for i in torpedoes:
            i.explode()
    if keys[pygame.K_UP]:
        target_fps *= 1.1
    if keys[pygame.K_DOWN]:
        target_fps /= 1.1

    if pygame.mouse.get_pressed()[0] and p.energy > 0:
        if p.current_weapon == 0:
            p.laser_on = True
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
            p.laser_on = False
            if frame % p.fire_rate == 0:
                p.fire_point_defense(get_angle_to_point(750,500,mouse_pos[0],mouse_pos[1])
                                     + random.randint(-10,10)/10)



    else:
        p.laser_on = False



    # --- Main event loop
    for event in pygame.event.get():  # User did something
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and p.energy > 0:
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

    if p.energy <= 0:
        p.stop_engine()
        p.laser_on = False


    # If there are more than a thousand projectiles in the world, the oldest will be deleted
    while len(globals.globals_dict["bullets"]) > 1000:
        globals.globals_dict["bullets"].pop(0)

    if len(enemies) < 1:
        enemies.append(Enemy(random.randint(round(camera_pos[0]), round(camera_pos[0]+1200)),
                             random.randint(round(camera_pos[1]), round(camera_pos[1]+800)),
                             (p.vx + random.randint(-20, 20)/10), (p.vy + random.randint(-20, 20)/10)))



    for i in range(len(enemies)):
        for b in globals.globals_dict["bullets"]:
            if enemies[i].alive and enemies[i].rect.colliderect(b.rect):
                enemies[i].health -= 2
                globals.globals_dict["bullets"].remove(b)


        for t in torpedoes:
            if not t.exploding:
                if t.parent != i:
                    if t.rect.colliderect(enemies[i].rect):
                        t.explode()
            if t.exploding and pygame.Mask(enemies[i].rect.size, True).overlap(t.mask,
                    (t.x-t.display_image.get_width()/2 -(enemies[i].x - enemies[i].display_image.get_width()/2),
                     (t.y-t.display_image.get_height()/2) - (enemies[i].y - enemies[i].display_image.get_height()/2))):
                enemies[i].health -= 25

    for b in globals.globals_dict["bullets"]:
        if p.mask.overlap(pygame.Mask((1,1), True), (b.x-(p.x-p.display_image.get_width()/2), b.y - (p.y - p.display_image.get_height()/2)))\
                and (b.parent != -1 or b.start_frame + 30 <= frame):

            p.health -= 2
            print(p.health)
            globals.globals_dict["bullets"].remove(b)

    for t in torpedoes:
        if not t.exploding:
            if t.parent != -1:
                if p.mask.overlap(pygame.Mask((1,1), True), (t.x-(p.x-p.display_image.get_width()/2), t.y - (p.y - p.display_image.get_height()/2))):
                    t.explode()
            for b in globals.globals_dict["bullets"]:
                if t.rect.colliderect(b.rect):
                    t.explode()
        if t.exploding and p.mask.overlap(t.mask,
                    (t.x - t.display_image.get_width() / 2 - (p.x - p.display_image.get_width() / 2),
                        (t.y - t.display_image.get_height() / 2) - (p.y - p.display_image.get_height() / 2))):
            p.health -= 25
            print(p.health)


    display_x = my_font.render(str(enemies[0].vx), True, (255,255,255))
    display_y = my_font.render(str(enemies[0].vy), True, (255,255,255))

    # display_x = my_font.render(str(enemies[0].cw), True, (255,255,255))
    # display_y = my_font.render(str(enemies[0].ccw), True, (255,255,255))
    display_fps = my_font.render(str(round(sum(fps_list)/len(fps_list))) + "/" + str(target_fps), True, (255,255,255))
    screen.fill((0, 0, 0))

    health_bar = pygame.Rect(10, 200+(1000 -p.health)/5, 10, p.health/5)
    energy_bar = pygame.Rect(25, 200+(1000 -p.energy)/5, 10, p.energy/5)

    # ------Blit Zone Start------

    if p.laser_on:
        # screen.blit(laser_image_transformed, laser_rect)
        pygame.draw.line(screen, (15,225,15), (750, 500), (750 + -1000 * math.sin(math.radians(p.angle)),
                                                         500 + -1000 *math.cos(math.radians(p.angle))), width=5)
        for i in enemies:
            if i.alive and i.mask.overlap(laser_mask, (laser_rect.left-i.rect.left,laser_rect.top -i.rect.top)):
                i.health -= 5

    for i in globals.globals_dict["bullets"]:
        pygame.draw.rect(screen, (255,150,50), pygame.Rect(i.x - camera_pos[0], i.y -camera_pos[1], 1,1))

    screen.blit(p.display_image, p.rect)


    for i in enemies:
        if i.alive:
            screen.blit(i.display_image, i.rect)

    for t in torpedoes:
        screen.blit(t.display_image, t.rect)

    screen.blit(display_x, (0, 0))
    screen.blit(display_y, (0, 15))
    screen.blit(display_fps, (0, size[1]-30))

    # screen.blit(i, (100-p.x, 100-p.y))

    pygame.draw.rect(screen, (0,255,0), health_bar)
    pygame.draw.rect(screen, (255, 255, 0), energy_bar)

    # ------Blit Zone End------

    pygame.display.update()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()


