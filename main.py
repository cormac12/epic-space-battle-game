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

def line_vector_collision(line_start, line_end, vector_start, vector_angle):
    angle_to_start = get_angle_to_point(vector_start[0], vector_start[1], line_start[0], line_start[1])
    angle_to_end = get_angle_to_point(vector_start[0], vector_start[1], line_end[0], line_end[1])
    if abs(angle_to_end - angle_to_start) < 180:
        return min(angle_to_start, angle_to_end) <= vector_angle <= max(angle_to_start, angle_to_end)
    else:
        return not min(angle_to_start, angle_to_end) <= vector_angle <= max(angle_to_start, angle_to_end)

def get_cross_section(mask, mask_coords, point):
    # returns the line from the two points in the mask with the most extreme angles, relative to point
    outline = mask.outline()
    angles = []
    for i in outline:
        angles.append(get_angle_to_point(point[0], point[1], mask_coords[0] + i[0], mask_coords[1] + i[1]))
    min_angle = angles[0]
    max_angle = angles[0]

    min_index = 0
    max_index = 0

    for i in range(len(angles)):
        if angles[i] < min_angle:
            min_angle = angles[i]
            min_index = i
        if angles[i] > max_angle:
            max_angle = angles[i]
            max_index = i
    return (outline[min_index], outline[max_index])



# set up pygame modules
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Arial', 15)
pygame.display.set_caption("Space Fight!")

# set up variables for the display
size = (1500, 1000)
screen = pygame.display.set_mode(size)


score = 0
display_score = my_font.render("Score: " + str(score), True, (255, 255, 255))

# The loop will carry on until the user exits the game (e.g. clicks the close button).
run = True

p = Player()



camera_pos = (0,0)

globals.globals_dict["player_x"] = p.x
globals.globals_dict["player_y"] = p.y
globals.globals_dict["camera_pos"] = camera_pos
globals.globals_dict["frame"] = 0
globals.globals_dict["bullets"] = []

enemies = [Enemy(100, 100, 2, 2, 1), Enemy(200, 200, 2, 2, 0)]
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

    line = get_cross_section(enemies[0].mask, (enemies[0].x - enemies[0].display_image.get_width()/2,
                                               enemies[0].y - enemies[0].display_image.get_height()/2,), (p.x, p.y))
    print(line_vector_collision(line[0], line[1], (p.x, p.y), p.angle))

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
            if e.ai_mode == 0:
                if e.get_distance_to_player() > 300:
                    e.target_vector(e.get_angle_to_player(), 2, p.vx, p.vy)
                elif e.get_distance_to_player() < 150:
                    e.target_vector(e.get_angle_to_player() + 180, 2, p.vx, p.vy)
                else:
                    e.target_vector(e.get_angle_to_player() + 60, 6, p.vx, p.vy)
                if frame > e.torpedo_cool_down_start + e.torpedo_cool_down_duration and random.randint(1,120) == 1:
                    e.ai_mode = 1
            elif e.ai_mode == 1:
                e.target_vector(e.get_angle_to_player(), 0, p.vx, p.vy)
                if p.vx - .5 <= e.vx <= p.vx + .5 and p.vy - .5 <= e.vy <= p.vy + .5:
                    torpedoes.append(Torpedo(e.x, e.y, e.vx, e.vy, e.get_angle_to_player(), False, -1, i))
                    e.torpedo_cool_down_start = frame
                    e.ai_mode = 0
            elif e.ai_mode == 2:
                if e.get_distance_to_player() < 700:
                    e.stop_engine()
                    e.target_direction(e.get_angle_to_player())

                else:
                    e.ai_mode = 3
            elif e.ai_mode == 3:
                if not e.get_distance_to_player() < 700:
                    e.target_vector(e.get_angle_to_player(), 3, p.vx, p.vy)
                else:
                    e.ai_mode = 4
            elif e.ai_mode == 4:
                if math.sqrt((e.vx - p.vx)**2 + (e.vy - p.vy)**2) > 1:
                    e.target_vector(e.get_angle_to_player(), 0, p.vx, p.vy)
                else:
                    e.ai_mode = 2

        else:
            enemies.pop(i)
        i += 1

    for i in globals.globals_dict["bullets"]:
        i.update()


    keys = pygame.key.get_pressed()
    if not p.power_off:
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

    if pygame.mouse.get_pressed()[0] and not p.power_off:
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
        elif p.current_weapon == 2:
            p.laser_on = False
            if p.last_railgun_time + p.railgun_cooldown <= frame:
                p.fire_railgun(get_angle_to_point(750,500,mouse_pos[0],mouse_pos[1])
                                     + random.randint(-10,10)/10)



    else:
        p.laser_on = False



    # --- Main event loop
    for event in pygame.event.get():  # User did something
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and not p.power_off:
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

    if p.power_off:
        p.stop_engine()
        p.laser_on = False


    # If there are more than a thousand projectiles in the world, the oldest will be deleted
    while len(globals.globals_dict["bullets"]) > 1000:
        globals.globals_dict["bullets"].pop(0)

    if score <= 2000 and len(enemies) < 1:
        enemies.append(Enemy(random.randint(round(camera_pos[0]), round(camera_pos[0]+1200)),
                             random.randint(round(camera_pos[1]), round(camera_pos[1]+800)),
                             (p.vx + random.randint(-20, 20)/10), (p.vy + random.randint(-20, 20)/10), 0))
        score += 1000
        display_score = my_font.render("Score: " + str(score), True, (255, 255, 255))
    elif 2000 < score and len(enemies) < 2:
        enemies.append(Enemy(random.randint(round(camera_pos[0]), round(camera_pos[0]+1200)),
                             random.randint(round(camera_pos[1]), round(camera_pos[1]+800)),
                             (p.vx + random.randint(-20, 20)/10), (p.vy + random.randint(-20, 20)/10), 0))
        score += 1000
        display_score = my_font.render("Score: " + str(score), True, (255, 255, 255))



    for i in range(len(enemies)):
        for b in globals.globals_dict["bullets"]:
            if enemies[i].alive and enemies[i].rect.colliderect(b.rect):
                enemies[i].health -= b.damage
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

            p.health -= b.damage
            globals.globals_dict["bullets"].remove(b)


    for t in torpedoes:
        if not t.exploding:
            if t.parent != -1:
                if p.mask.overlap(pygame.Mask((1,1), True), (t.x-(p.x-p.display_image.get_width()/2), t.y - (p.y - p.display_image.get_height()/2))):
                    t.explode()
            for b in globals.globals_dict["bullets"]:
                if t.rect.colliderect(b.rect):
                    t.explode()
            if p.laser_on:
                if laser_mask.overlap(pygame.mask.from_surface(t.display_image),
                        (t.rect.x - t.display_image.get_width() / 2 - (laser_rect.x),
                            (t.rect.y - t.display_image.get_height() / 2) - (laser_rect.y))):
                    t.explode()
        if t.exploding and p.mask.overlap(t.mask,
                    (t.x - t.display_image.get_width() / 2 - (p.x - p.display_image.get_width() / 2),
                        (t.y - t.display_image.get_height() / 2) - (p.y - p.display_image.get_height() / 2))):
            p.health -= 25






    display_fps = my_font.render(str(round(sum(fps_list)/len(fps_list))) + "/" + str(target_fps), True, (255,255,255))
    screen.fill((0, 0, 0))

    health_bar = pygame.Rect(10, 200+(1000 -p.health)/5, 10, p.health/5)
    energy_bar = pygame.Rect(25, 200+(1000 -p.energy)/5, 10, p.energy/5)

    # ------Blit Zone Start------

    if p.laser_on:
        pygame.draw.line(screen, (15,225,15), (750, 500), (750 + -1000 * math.sin(math.radians(p.angle)),
                                                         500 + -1000 *math.cos(math.radians(p.angle))), width=5)
        for i in enemies:
            if i.alive and i.mask.overlap(laser_mask, (laser_rect.left-i.rect.left,laser_rect.top -i.rect.top)):
                i.health -= 5

    for i in globals.globals_dict["bullets"]:
        pygame.draw.rect(screen, i.color, i.rect)

    screen.blit(p.display_image, p.rect)


    for i in enemies:
        if i.alive:
            screen.blit(i.display_image, i.rect)

    for t in torpedoes:
        screen.blit(t.display_image, t.rect)


    screen.blit(display_fps, (0, size[1]-30))
    screen.blit(display_score, (0,0))
    # screen.blit(i, (100-p.x, 100-p.y))

    pygame.draw.rect(screen, (0,255,0), health_bar)
    if p.power_off:
        pygame.draw.rect(screen, (255, 0, 0), energy_bar)


    else:
        pygame.draw.rect(screen, (100, 150, 255), energy_bar)

    # ------Blit Zone End------

    pygame.display.update()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()


