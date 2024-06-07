import pygame
from player import Player
import globals
from enemy import Enemy
import random
import time
import math
from torpedo import Torpedo
from laser import Laser
from bullet import Bullet


def get_angle_to_point(x1,y1, x2, y2):
    if y1 - y2 != 0:
        if x1 >= x2 and y1 >= y2:
            return math.degrees(math.atan((x1 - x2) / (y1 - y2))) % 360
        elif x1 >= x2 and y1 <= y2:
            return (math.degrees((math.atan((x1 - x2) / (y1 - y2)))) + 180) % 360
        elif x1 <= x2 and y1 <= y2:
            return (math.degrees((math.atan((x1 - x2) / (y1 - y2)))) + 180) % 360
        elif x1 <= x2 and y1 >= y2:
            return math.degrees(math.atan((x1 - x2) / (y1 - y2))) % 360
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

def get_mask_cross_section(mask, mask_coords, point):
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
    return ((outline[min_index][0] + mask_coords[0], outline[min_index][1] + mask_coords[1]),
            ((outline[max_index][0] + mask_coords[0], outline[max_index][1] + mask_coords[1])))

def get_rect_cross_section(rect, rect_coords, point):
    corners = [rect_coords, (rect_coords[0] + rect.width, rect_coords[1]),
                (rect_coords[0], rect_coords[1] + rect.height),
                (rect_coords[0] + rect.width, rect_coords[1] + rect.height)]
    angles = []
    for i in corners:
        angles.append(get_angle_to_point(point[0], point[1], i[0], i[1]))
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
    return ((corners[min_index][0], corners[min_index][1]), ((corners[max_index][0], corners[max_index][1])))


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

radar_image = pygame.image.load("radar.png")
player_icon = pygame.image.load("player icon.png")

# The loop will carry on until the user exits the game (e.g. clicks the close button).
run = True

p = Player()



camera_pos = (0,0)

globals.globals_dict["player_x"] = p.x
globals.globals_dict["player_y"] = p.y
globals.globals_dict["camera_pos"] = camera_pos
globals.globals_dict["frame"] = 0
globals.globals_dict["bullets"] = []
globals.globals_dict["lasers"] = [Laser((p.x, p.y), p.angle, 5, (10, 255, 10), 4, -1)]

enemies = [Enemy(100, 100, 2, 2, 1, 0), Enemy(200, 200, 2, 2, 0, 1)]
torpedoes = []

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
                    if e.last_laser_time + 60 < frame:
                        if e.sweep_direction == 0:
                            e.sweep_direction = -1 if random.randint(0,1) == 0 else 1
                        if not e.laser_is_on:
                            if e.target_direction(e.get_angle_to_player()+ -15 * e.sweep_direction):
                                e.laser_is_on = True
                                e.start_angle = e.angle
                        if e.laser_is_on:
                            e.rotate("clockwise" if e.sweep_direction == -1 else "counterclockwise")
                            if e.sweep_direction == 1 and e.angle > (e.start_angle + 30) % 360 or e.sweep_direction == -1 and e.angle < (e.start_angle - 30) %360:
                                e.laser_is_on = False
                                e.last_laser_time = frame
                                e.sweep_direction = 0
                                print("Done")


                else:
                    e.ai_mode = 3
            elif e.ai_mode == 3:
                e.laser_is_on = False
                e.last_laser_time = frame
                e.sweep_direction = 0
                if not e.get_distance_to_player() < math.sqrt((e.vx - p.vx)**2 + (e.vy - p.vy)**2)**(2)*15:
                    e.target_vector(e.get_angle_to_player(), e.get_distance_to_player()/250, p.vx, p.vy)
                else:
                    e.ai_mode = 4
            elif e.ai_mode == 4:
                e.laser_is_on = False
                e.last_laser_time = frame
                e.sweep_direction = 0
                if math.sqrt((e.vx - p.vx)**2 + (e.vy - p.vy)**2) > 1:
                    e.target_vector(e.get_angle_to_player(), 0, p.vx, p.vy)
                else:
                    e.ai_mode = 2

        else:
            if e.type == 1:
                globals.globals_dict["lasers"].pop(e.laser_index)
            enemies.pop(i)
            for x in range(len(enemies)):
                if x > i:
                    enemies[x].index -= 1
            for x in range(len(globals.globals_dict["lasers"])):
                if globals.globals_dict["lasers"][x].parent > i:
                    globals.globals_dict["lasers"][x].parent -= 1
        i += 1

    for l in globals.globals_dict["lasers"]:
        if l.parent != -1:
            l.set_angle(enemies[l.parent].angle)
            l.set_pos(enemies[l.parent].x, enemies[l.parent].y)
            l.is_on = enemies[l.parent].laser_is_on



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

    player_icon_display = pygame.transform.rotate(player_icon, p.angle)

    globals.globals_dict["lasers"][0].set_angle(p.angle)
    globals.globals_dict["lasers"][0].set_pos(p.x, p.y)

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
                             (p.vx + random.randint(-20, 20)/10), (p.vy + random.randint(-20, 20)/10), 1, len(enemies)))
        score += 1000
        display_score = my_font.render("Score: " + str(score), True, (255, 255, 255))
    elif 2000 < score and len(enemies) < 2:
        enemies.append(Enemy(random.randint(round(camera_pos[0]), round(camera_pos[0]+1200)),
                             random.randint(round(camera_pos[1]), round(camera_pos[1]+800)),
                             (p.vx + random.randint(-20, 20)/10), (p.vy + random.randint(-20, 20)/10), 1, len(enemies)))
        score += 1000
        display_score = my_font.render("Score: " + str(score), True, (255, 255, 255))

    globals.globals_dict["lasers"][0].is_on = p.laser_on

    enemy_index = -1

    for l in globals.globals_dict["lasers"]:
        if l.is_on:
            for e in enemies:
                enemy_index += 1
                if l.parent != enemy_index:
                    has_been_hit = False
                    if e.type == 1:
                        for v in l.vectors:
                            cross_section = get_mask_cross_section(e.mask, (e.x-e.display_image.get_width()/2,
                                                                            e.y - e.display_image.get_height()/2), v[0])
                            if line_vector_collision(cross_section[0], cross_section[1], v[0], v[1]) and not has_been_hit:
                                e.health -= l.damage
                                has_been_hit = True
                    elif e.type == 0:  # type 0 enemies are so small that you can't really tell that I use rect collision
                        for v in l.vectors:
                            cross_section = get_rect_cross_section(e.rect, (e.x-e.display_image.get_width()/2,
                                                                            e.y - e.display_image.get_height()/2), v[0])
                            if line_vector_collision(cross_section[0], cross_section[1], v[0], v[1]) and not has_been_hit:
                                e.health -= l.damage
                                has_been_hit = True
            for t in torpedoes:
                if not t.exploding:
                    for v in l.vectors:
                        cross_section = get_rect_cross_section(t.rect, (t.x - t.display_image.get_width()/2,
                                                                        t.y - t.display_image.get_height()/2), v[0])
                        if line_vector_collision(cross_section[0], cross_section[1], v[0], v[1]):
                            t.explode()


            has_been_hit = False
            if l.parent != -1:
                for v in l.vectors:
                    cross_section = get_mask_cross_section(p.mask, (p.x - p.display_image.get_width() / 2,
                                                                    p.y - p.display_image.get_height() / 2), v[0])
                    if line_vector_collision(cross_section[0], cross_section[1], v[0], v[1]) and not has_been_hit:
                        p.health -= l.damage
                        has_been_hit = True




    for i in range(len(enemies)):
        for b in globals.globals_dict["bullets"]:
            if enemies[i].type == 0:
                if enemies[i].alive and enemies[i].rect.colliderect(b.rect) and (b.parent != e.index or b.start_frame + 30 <= frame):
                    enemies[i].health -= b.damage
                    globals.globals_dict["bullets"].remove(b)
            elif enemies[i].type == 1:
                if (enemies[i].alive and enemies[i].mask.overlap(pygame.Mask(b.size, True), (b.x - (enemies[i].x - enemies[i].display_image.get_width()/2),
                                                                                            b.y - (enemies[i].y - enemies[i].display_image.get_height()/2))) and
                        (b.parent != e.index or b.start_frame + 30 <= frame)):
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
        if p.mask.overlap(pygame.Mask(b.size, True), (b.x-(p.x-p.display_image.get_width()/2), b.y - (p.y - p.display_image.get_height()/2)))\
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
        if t.exploding and p.mask.overlap(t.mask,
                    (t.x - t.display_image.get_width() / 2 - (p.x - p.display_image.get_width() / 2),
                        (t.y - t.display_image.get_height() / 2) - (p.y - p.display_image.get_height() / 2))):
            p.health -= 25






    display_fps = my_font.render(str(round(sum(fps_list)/len(fps_list))) + "/" + str(target_fps), True, (255,255,255))
    screen.fill((0, 0, 0))

    health_bar = pygame.Rect(10, 200+(1000 -p.health)/5, 10, p.health/5)
    energy_bar = pygame.Rect(25, 200+(1000 -p.energy)/5, 10, p.energy/5)

    # ------Blit Zone Start------

    for l in globals.globals_dict["lasers"]:
        if l.is_on:
            start_pos = (l.origin[0] - camera_pos[0], l.origin[1] - camera_pos[1])
            if l.angle == 0:
                end_pos = (start_pos[0], -10)
            elif l.angle == 90:
                end_pos = (-10, start_pos[1])
            elif l.angle == 180:
                end_pos = (start_pos[0], size[1] + 10)
            elif l.angle == 270:
                end_pos = (size[0] + 10, start_pos[1])
            elif l.angle < 180:
                end_pos = (-10, start_pos[1] - (1/math.tan(math.radians(l.angle)) * (start_pos[0] + 10)))
            else:
                end_pos = (size[0] + 10, start_pos[1] + (1/math.tan(math.radians(l.angle)) * ( size[0] + 10 - start_pos[0])))


            pygame.draw.line(screen, l.color, start_pos, end_pos, l.width)

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

    screen.blit(radar_image, (5,size[1]-260))
    screen.blit(player_icon_display, (132.5-player_icon_display.get_width()/2, size[1]-132.5-player_icon_display.get_height()/2))
    for e in enemies:
        if e.get_distance_to_player() < 5400:
            pygame.draw.rect(screen, (255,0,0), pygame.Rect(132.5+math.sin(math.radians(e.get_angle_to_player()))*(e.get_distance_to_player()/50+6.5),
                                                            size[1]-132.5+math.cos(math.radians(e.get_angle_to_player()))*(e.get_distance_to_player()/50+6.5), 4,4))

    # ------Blit Zone End------

    pygame.display.update()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()


