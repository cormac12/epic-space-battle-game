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
arial = pygame.font.SysFont('Arial', 16)
impact = pygame.font.SysFont("Impact", 48)
pygame.display.set_caption("Space Fight!")

# set up variables for the display
size = (1500, 1000)
screen = pygame.display.set_mode(size)

game_state = 0
# state 0 is menu screen.
# state 1 is main game.
# state 2 is game over



wave = 0

wave_text = impact.render("WAVE " + str(wave), True, (255,255,255))
wave_rect = pygame.Rect(size[0]/2-wave_text.get_width()/2, size[1]/4 - wave_text.get_height()/2, wave_text.get_width(), wave_text.get_height())
wave_text_start = -1000

tutorial_stage = 0
tutorial_texts = ["Use A/D to rotate your spaceship, and W to fly forward.",
                  "Try flying through that red circle. There's no friction in space, so the controls will feel a bit slippery at first.",
                  "You can use the scroll wheel to select a weapon, and left click to fire.",
                  "Destroy the red circle to continue."]

skip_tutorial_text = arial.render("Press space to skip the tutorial.", True, (255,255,255))

has_clicked = False
has_scrolled = False


gunships = 1
fighters = 1


radar_image = pygame.image.load("radar.png")
player_icon = pygame.image.load("player icon.png")
arrow = pygame.image.load("arrow.png")

icons = [pygame.image.load("laser icon.png"), pygame.image.load("machine gun icon.png"),pygame.image.load("railgun icon.png")]
weapon_names = ["Laser", "Machine Gun", "Railgun"]
weapon_names_rendered = []

health_icon = pygame.image.load("health icon.png")
energy_icon = pygame.image.load("energy icon.png")
for i in weapon_names:
    weapon_names_rendered.append(arial.render(i, True, (255,255,255)))

# The loop will carry on until the user exits the game (e.g. clicks the close button).
run = True

p = Player()

title_text = impact.render("  EPIC SPACE BATTLE GAME!  ", True, (255,255,0))
title_rect = pygame.Rect(size[0]/2-title_text.get_width()/2, size[1]/4-title_text.get_height()/2,
                                title_text.get_width(), title_text.get_height()
                                )

title_screen_image_1 = pygame.transform.scale_by(pygame.image.load("spaceship.png", ), 2)
title_screen_rect_1 = pygame.Rect(size[0]/2 - title_rect.width/2 - title_screen_image_1.get_width(),
                                  size[1]/4 - title_screen_image_1.get_height()/2, title_screen_image_1.get_width(),
                                  title_screen_image_1.get_height())

title_screen_image_2 = pygame.transform.scale(pygame.image.load("gunship 11.png", ), (111,166))
title_screen_rect_2 = pygame.Rect(size[0]/2 + title_rect.width/2,
                                  size[1]/4 - title_screen_image_2.get_height()/2, title_screen_image_2.get_width(),
                                  title_screen_image_2.get_height())

start_button_text = impact.render(" START ", True, (0,0,0))
start_button_rect = pygame.Rect(size[0]/2-start_button_text.get_width()/2, size[1]/2-start_button_text.get_height()/2,
                                start_button_text.get_width(), start_button_text.get_height()
                                )

game_over_text = impact.render("GAME OVER", True, (255,0,0))
game_over_rect = pygame.Rect(size[0]/2-game_over_text.get_width()/2, size[1]/4-game_over_text.get_height()/2,
                                game_over_text.get_width(), game_over_text.get_height())
final_wave_text = None



camera_pos = (0,0)

globals.globals_dict["player_x"] = p.x
globals.globals_dict["player_y"] = p.y
globals.globals_dict["camera_pos"] = camera_pos
globals.globals_dict["frame"] = 0
globals.globals_dict["bullets"] = []


enemies = [Enemy(1000, 500, 0, 0, 2, 0)]
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



    if game_state == 0:
        # --- Main event loop
        for event in pygame.event.get():  # User did something
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] and start_button_rect.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                    game_state = 1



            elif event.type == pygame.QUIT:  # If user clicked close
                run = False

        #Blit Zone Start:
        pygame.draw.rect(screen, (255,255,255), start_button_rect)
        screen.blit(start_button_text, start_button_rect)
        screen.blit(title_text, title_rect)
        screen.blit(title_screen_image_1, title_screen_rect_1)
        screen.blit(title_screen_image_2, title_screen_rect_2)

    elif game_state == 1:
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

        # updating torpedoes
        for t in torpedoes:
            t.update()
            if not t.exploding and frame > t.start_frame + 150:
                t.explode()
            if not t.alive:
                torpedoes.remove(t)


        # updating enemies
        i = 0
        for e in enemies:
            if e.alive:
                e.update()
                if e.ai_mode == 0:
                    if e.get_distance_to_player() > 500:
                        e.target_vector(e.get_angle_to_player(), e.get_distance_to_player()/100, p.vx, p.vy)
                    elif e.get_distance_to_player() < 150:
                        e.target_vector(e.get_angle_to_player() + 180, 2, p.vx, p.vy)
                    else:
                        e.target_vector(e.get_angle_to_player()+70, 5, p.vx, p.vy)
                    if frame > e.torpedo_cool_down_start + e.torpedo_cool_down_duration and random.randint(1,120) == 1\
                            and e.get_distance_to_player() < 500:
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


                    else:
                        e.ai_mode = 3
                elif e.ai_mode == 3:
                    e.laser_is_on = False
                    e.last_laser_time = frame
                    e.sweep_direction = 0
                    if not (e.get_distance_to_player() < math.sqrt((e.vx - p.vx)**2 + (e.vy - p.vy)**2)**(2)*15 or e.get_distance_to_player() <= 500):
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

                if e.type == 1:
                    e.laser.set_angle(e.angle)
                    e.laser.set_pos(e.x, e.y)
                    e.laser.is_on = e.laser_is_on

                first_loop = True
                if e.type == 0:

                    while p.mask.overlap(pygame.Mask((e.rect.width, e.rect.height), True), (e.rect.x - p.rect.x, e.rect.y - p.rect.y)):
                        e.move(1 * (p.mass/(p.mass+e.mass)), e.get_angle_to_player() + 180)
                        p.move(1 * (e.mass/(p.mass+e.mass)), e.get_angle_to_player())
                        if first_loop:
                            velocity_diff = math.sqrt((e.vx - p.vx)**2 + (e.vy - p.vy)**2)
                            bounce_strength = velocity_diff * 0.25
                            e.change_velocity(bounce_strength * (p.mass/(p.mass+e.mass)), e.get_angle_to_player() + 180)
                            p.change_velocity(bounce_strength * (e.mass / (p.mass + e.mass)), e.get_angle_to_player())
                            first_loop = False

                elif e.type == 1:
                    while p.mask.overlap(e.mask, (e.rect.x - p.rect.x, e.rect.y - p.rect.y)):
                        e.move(1 * (p.mass/(p.mass+e.mass)), e.get_angle_to_player() + 180)
                        p.move(1 * (e.mass/(p.mass+e.mass)), e.get_angle_to_player())
                        if first_loop:
                            velocity_diff = math.sqrt((e.vx - p.vx)**2 + (e.vy - p.vy)**2)
                            bounce_strength = velocity_diff * 0.25
                            e.change_velocity(bounce_strength * (p.mass/(p.mass+e.mass)), e.get_angle_to_player() + 180)
                            p.change_velocity(bounce_strength * (e.mass / (p.mass + e.mass)), e.get_angle_to_player())
                            first_loop = False


                for a in enemies:
                    if e != a:
                        if e.type == 0:
                            if a.type == 0:
                                while e.rect.colliderect(a.rect):
                                    e.move(a.mass/(e.mass+a.mass), get_angle_to_point(a.x, a.y, e.x, e.y))
                                    a.move(e.mass / (e.mass + a.mass), get_angle_to_point(e.x, e.y, a.x, a.y))

                            elif a.type == 1:
                                while a.mask.overlap(pygame.Mask(e.rect.size, True),
                                                     (e.rect.x - a.rect.x, e.rect.y-a.rect.y)
                                                     ):
                                    e.move(a.mass/(e.mass+a.mass), get_angle_to_point(a.x, a.y, e.x, e.y))
                                    a.move(e.mass / (e.mass + a.mass), get_angle_to_point(e.x, e.y, a.x, a.y))
                        elif e.type == 1:
                            if a.type == 1:
                                while a.mask.overlap(a.mask,
                                                     (e.rect.x - a.rect.x, e.rect.y-a.rect.y)
                                                     ):
                                    e.move(a.mass/(e.mass+a.mass), get_angle_to_point(a.x, a.y, e.x, e.y))
                                    a.move(e.mass / (e.mass + a.mass), get_angle_to_point(e.x, e.y, a.x, a.y))

            else:

                enemies.remove(e)
                for x in range(len(enemies)):
                    if x >= i:
                        enemies[x].index -= 1
                for t in range(len(torpedoes)):
                    if torpedoes[t].parent == i:
                        torpedoes[t].explode()
                    elif torpedoes[t].parent > i:
                        torpedoes[t].parent -= 1
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

        player_icon_display = pygame.transform.rotate(player_icon, p.angle)



        if keys[pygame.K_SPACE]:
            fps = 1
            for i in torpedoes:
                i.explode()
        if keys[pygame.K_UP]:
            target_fps *= 1.1
        if keys[pygame.K_DOWN]:
            target_fps /= 1.1

        # weapon firing
        if pygame.mouse.get_pressed()[0] and not p.power_off and tutorial_stage >= 2:
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

        p.laser.is_on = p.laser_on
        p.laser.set_pos(p.x,p.y)
        p.laser.set_angle(p.angle)

        # --- Main event loop
        for event in pygame.event.get():  # User did something
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and not p.power_off:
                    p.start_engine()
                elif event.key == pygame.K_SPACE and tutorial_stage < 4:
                    tutorial_stage = 4
                    enemies = []
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    p.stop_engine()
            elif event.type == pygame.MOUSEWHEEL:
                if tutorial_stage >= 2:
                    has_scrolled = True
                    if event.y > 0 and p.current_weapon < len(weapon_names)-1:
                        p.current_weapon += 1
                    elif event.y < 0 and p.current_weapon > 0:
                        p.current_weapon -= 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if tutorial_stage == 2:
                        has_clicked = True
                elif event.button == 3:
                    enemies = []


            elif event.type == pygame.QUIT:  # If user clicked close
                run = False

        if p.power_off:
            p.stop_engine()
            p.laser_on = False


        # If there are more than 500 projectiles in the world, the oldest will be deleted
        while len(globals.globals_dict["bullets"]) > 500:
            globals.globals_dict["bullets"].pop(0)


        # enemy respawns
        if len(enemies) == 0 and tutorial_stage == 4:
            wave += 1

            wave_text = impact.render("WAVE " + str(wave), True, (255, 255, 255))
            wave_rect = pygame.Rect(size[0] / 2 - wave_text.get_width() / 2, size[1] / 4 - wave_text.get_height() / 2,
                                    wave_text.get_width(), wave_text.get_height())
            wave_text_start = frame

            for i in range(int(fighters//1)):
                angle = random.randint(1,360)
                distance = random.randint(1000, 3000)
                x = p.x - math.sin(angle)*distance
                y = p.y - math.cos(angle)*distance
                enemies.append(Enemy(x, y,
                                     (p.vx + random.randint(-20, 20)/10), (p.vy + random.randint(-20, 20)/10), 0, len(enemies)))
            for i in range(int(gunships//1)):
                angle = random.randint(1,360)
                distance = random.randint(1000, 1500)
                x = p.x - math.sin(angle)*distance
                y = p.y - math.cos(angle)*distance
                enemies.append(Enemy(x, y,
                                     (p.vx + random.randint(-20, 20)/10), (p.vy + random.randint(-20, 20)/10), 1, len(enemies)))

            if gunships < 30:
                gunships += .5
            if fighters < 50:
                fighters += 1





        # enemy lasers
        for i in enemies:
            if i.type == 1:
                l = i.laser
                if l.is_on:
                    for e in enemies:
                        angle = get_angle_to_point(l.origin[0], l.origin[1], e.x, e.y)
                        if (angle >= (l.angle - 90) % 360 or angle >= (l.angle - 90)) and (
                                angle <= (l.angle + 90) or (l.angle + 90 > 360
                                                            and angle <= (l.angle + 90) % 360)):

                            if i != e:
                                if e.type == 1:
                                    if l.collide_rect(e.rect, (e.x - e.display_image.get_width() / 2,
                                                               e.y - e.display_image.get_height() / 2)):
                                        if l.collide_mask(e.mask, (e.x - e.display_image.get_width() / 2,
                                                                   e.y - e.display_image.get_height() / 2)):
                                            e.health -= l.damage
                                elif e.type == 0:  # type 0 enemies are so small that you can't really tell that I use rect collision
                                    if l.collide_rect(e.rect, (e.x - e.display_image.get_width() / 2,
                                                               e.y - e.display_image.get_height() / 2)):
                                        e.health -= l.damage
                    for t in torpedoes:
                        angle = get_angle_to_point(l.origin[0], l.origin[1], t.x, t.y)
                        if (angle >= (l.angle - 90) % 360 or angle >= (l.angle - 90)) and (
                                angle <= (l.angle + 90) or (l.angle + 90 > 360
                                                                and angle <= (l.angle + 90) % 360)):
                            if not t.exploding:
                                if l.collide_rect(t.rect, (t.x-t.rect.width/2, t.y-t.rect.height/2)):
                                    t.explode()


                    angle = get_angle_to_point(l.origin[0], l.origin[1], p.x, p.y)
                    if (angle >= (l.angle - 90) % 360 or angle >= (l.angle - 90)) and (
                            angle <= (l.angle + 90) or (l.angle + 90 > 360
                                                        and angle <= (l.angle + 90) % 360)):

                        if l.collide_rect(p.rect, (p.x-p.rect.width/2, p.y-p.rect.height/2)):
                            if l.collide_mask(p.mask, (p.x - p.rect.width / 2, p.y - p.rect.height / 2)):
                                p.health -= l.damage


        # player laser
        l = p.laser
        if l.is_on:
            for e in enemies:
                angle = get_angle_to_point(l.origin[0], l.origin[1], e.x, e.y)
                if (angle >= (l.angle - 90) % 360 or angle >= (l.angle - 90)) and (angle <= (l.angle + 90) or (l.angle + 90 > 360
                                                                                                               and angle <= (l.angle + 90)%360)):

                    if e.type == 1 or e.type == 2:

                        if l.collide_rect(e.rect, (e.x - e.rect.width / 2, e.y - e.rect.height / 2)):
                            print("RECT")
                            if l.collide_mask(e.mask, (e.x - e.display_image.get_width() / 2,
                                                                                e.y - e.display_image.get_height() / 2)):
                                e.health-= l.damage
                                print(True)


                    elif e.type == 0:  # type 0 enemies are so small that you can't really tell that I use rect collision
                        if l.collide_rect(e.rect, (e.x - e.display_image.get_width() / 2,
                                                                            e.y - e.display_image.get_height() / 2)):
                            e.health -= l.damage


            for t in torpedoes:
                angle = get_angle_to_point(l.origin[0], l.origin[1], t.x, t.y)
                if (angle >= (l.angle - 90) % 360 or angle >= (l.angle - 90)) and (angle <= (l.angle + 90) or (l.angle + 90 > 360
                                                                                                               and angle <= (l.angle + 90)%360)):
                    if not t.exploding:
                        if l.collide_rect(t.rect, (t.x-t.rect.width/2, t.y-t.rect.height/2)):
                            t.explode()


        for i in range(len(enemies)):
            # enemy bullet collision
            for b in globals.globals_dict["bullets"]:
                if enemies[i].type == 0:
                    if enemies[i].alive and enemies[i].rect.colliderect(b.rect) and (b.parent != e.index or b.start_frame + 30 <= frame):
                        enemies[i].health -= b.damage
                        globals.globals_dict["bullets"].remove(b)
                elif enemies[i].type == 1 or enemies[i].type == 2:
                    if (enemies[i].alive and enemies[i].mask.overlap(pygame.Mask(b.size, True), (b.x - (enemies[i].x - enemies[i].display_image.get_width()/2),
                                                                                                b.y - (enemies[i].y - enemies[i].display_image.get_height()/2))) and
                            (b.parent != e.index or b.start_frame + 30 <= frame)):
                        enemies[i].health -= b.damage
                        globals.globals_dict["bullets"].remove(b)
            # enemy torpedo collision
            for t in torpedoes:
                if not t.exploding:
                    if t.parent != i:
                        if t.rect.colliderect(enemies[i].rect):
                            t.explode()
                if t.exploding and pygame.Mask(enemies[i].rect.size, True).overlap(t.mask,
                        (t.x-t.display_image.get_width()/2 -(enemies[i].x - enemies[i].display_image.get_width()/2),
                         (t.y-t.display_image.get_height()/2) - (enemies[i].y - enemies[i].display_image.get_height()/2))):
                    enemies[i].health -= 25





        # player bullet collision
        for b in globals.globals_dict["bullets"]:
            if p.mask.overlap(pygame.Mask(b.size, True), (b.x-(p.x-p.display_image.get_width()/2), b.y - (p.y - p.display_image.get_height()/2)))\
                    and (b.parent != -1 or b.start_frame + 30 <= frame):

                p.health -= b.damage
                globals.globals_dict["bullets"].remove(b)
        # player torpedo collision
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


        if p.health <= 0:
            game_state = 2

        if (p.vx != 0 or p.vy != 0) and tutorial_stage == 0:
            tutorial_stage = 1
        elif tutorial_stage == 1:
            if enemies[0].get_distance_to_player() < 40:
                tutorial_stage = 2
        elif tutorial_stage == 2 and (has_scrolled or has_clicked):
            tutorial_stage = 3
        elif tutorial_stage == 3 and len(enemies) == 0:
            tutorial_stage = 4


        display_fps = arial.render(str(round(sum(fps_list)/len(fps_list))) + "/" + str(target_fps), True, (255,255,255))
        screen.fill((0, 0, 0))

        health_bar = pygame.Rect(10, 200+(1000 -p.health)/5, 10, p.health/5)
        energy_bar = pygame.Rect(25, 200+(1000 -p.energy)/5, 10, p.energy/5)

        # ------Blit Zone Start------

        for e in enemies:
            if e.type == 1:
                l = e.laser
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

        l = p.laser
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
                end_pos = (-10, start_pos[1] - (1 / math.tan(math.radians(l.angle)) * (start_pos[0] + 10)))
            else:
                end_pos = (
                size[0] + 10, start_pos[1] + (1 / math.tan(math.radians(l.angle)) * (size[0] + 10 - start_pos[0])))

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
        # screen.blit(i, (100-p.x, 100-p.y))

        screen.blit(health_icon, (10, 185))
        screen.blit(energy_icon, (25, 185))

        pygame.draw.rect(screen, (237, 28, 36), health_bar)
        if p.power_off:
            pygame.draw.rect(screen, (237, 28, 36), energy_bar)



        else:
            pygame.draw.rect(screen, (0, 162, 232), energy_bar)

        screen.blit(radar_image, (5,size[1]-260))
        screen.blit(player_icon_display, (132.5-player_icon_display.get_width()/2, size[1]-132.5-player_icon_display.get_height()/2))
        for e in enemies:
            if e.get_distance_to_player() < 8100:
                pygame.draw.rect(screen, (255,0,0), pygame.Rect(132.5+math.sin(math.radians(e.get_angle_to_player()))*(e.get_distance_to_player()/75+6.5),
                                                                size[1]-132.5+math.cos(math.radians(e.get_angle_to_player()))*(e.get_distance_to_player()/75+6.5),
                                                                4,4))
            else:
                image = pygame.transform.rotate(arrow, e.get_angle_to_player()+180)
                rect = pygame.Rect(132.5+math.sin(math.radians(e.get_angle_to_player()))*116 - image.get_width()/2,
                                   size[1]-132.5+math.cos(math.radians(e.get_angle_to_player()))*116 - image.get_height()/2,
                                   1,1)
                screen.blit(image, rect)

        if tutorial_stage >= 2:
            for i in range(len(weapon_names)):
                x = size[0]- 105
                y = size[1]/2 - 60 - (i - 1)*120
                rect = pygame.Rect(x,y, 100,100)
                if p.current_weapon == i:
                    pygame.draw.rect(screen, (0, 150, 0), rect)
                else:
                    pygame.draw.rect(screen, (50,50,50), rect)
                screen.blit(icons[i], rect)
                screen.blit(weapon_names_rendered[i], (x,y+100))

        if tutorial_stage < len(tutorial_texts):
            text = arial.render(tutorial_texts[tutorial_stage], True, (255,255,255))
            screen.blit(text, (size[0]/2 - text.get_width()/2, 700))
            screen.blit(skip_tutorial_text, (size[0]/2 - skip_tutorial_text.get_width()/2, 700+18))

        if wave_text_start + 30 > frame:
            screen.blit(wave_text, wave_rect)



    elif game_state == 2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If user clicked close
                run = False
        if final_wave_text == None:
            final_wave_text = impact.render("YOU SURVIVED: " + str(wave - 1) + (" WAVE" if wave == 2 else " WAVES"),
                                            False, (255,255,255))
            final_wave_rect = pygame.Rect(size[0]/2-final_wave_text.get_width()/2, size[1]/2-final_wave_text.get_height()/2,
                                final_wave_text.get_width(), final_wave_text.get_height()
                                )
            # Blit Zone Start
            screen.blit(final_wave_text,final_wave_rect)
            screen.blit(game_over_text, game_over_rect)


    # ------Blit Zone End------

    pygame.display.update()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()


