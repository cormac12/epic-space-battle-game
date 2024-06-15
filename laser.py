import math

import pygame

import globals


class Laser:
    def __init__(self, origin, angle, width, color, damage, parent):
        self.origin = origin
        self.angle = angle
        self.width = width
        self.color = color
        self.damage = damage
        self.parent = parent
        self.is_on = False
        self.rays = []
        self.rays.append((self.origin, self.angle))
        self.rays.append(((self.origin[0] - math.cos(math.radians(angle)) * self.width/2,
                              self.origin[1] - math.sin(math.radians(angle)) * self.width/2), self.angle))
        self.rays.append(((self.origin[0] + math.cos(math.radians(angle)) * self.width/2,
                              self.origin[1] + math.sin(math.radians(angle)) * self.width/2), self.angle))
    
    def set_angle(self, angle):
        self.angle = angle
        self.rays = []
        self.rays.append((self.origin, self.angle))
        self.rays.append(((self.origin[0] - math.cos(math.radians(angle)) * self.width/2,
                              self.origin[1] - math.sin(math.radians(angle)) * self.width/2), self.angle))
        self.rays.append(((self.origin[0] + math.cos(math.radians(angle)) * self.width/2,
                              self.origin[1] + math.sin(math.radians(angle)) * self.width/2), self.angle))

    def set_pos(self, x, y):
        self.origin = (x, y)
        self.rays = []
        self.rays.append((self.origin, self.angle))
        self.rays.append(((self.origin[0] - math.cos(math.radians(self.angle)) * self.width/2,
                              self.origin[1] - math.sin(math.radians(self.angle)) * self.width/2), self.angle))
        self.rays.append(((self.origin[0] + math.cos(math.radians(self.angle)) * self.width/2,
                              self.origin[1] + math.sin(math.radians(self.angle)) * self.width/2), self.angle))


    def collide_rect(self, rect: pygame.Rect, rect_coords):

        corners = [rect_coords, (rect_coords[0] + rect.width, rect_coords[1]),
                   (rect_coords[0], rect_coords[1] + rect.height),
                   (rect_coords[0] + rect.width, rect_coords[1] + rect.height)]


        for r in self.rays:
            
            angles = []
            
            for corner in corners:
                angles.append(globals.get_angle_to_point(r[0][0], r[0][1], corner[0], corner[1]))

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
                    
            cross_section = (corners[min_index][0], corners[min_index][1]), (corners[max_index][0], corners[max_index][1])

            angle_to_start = globals.get_angle_to_point(r[0][0], r[0][1], cross_section[0][0], cross_section[0][1])
            angle_to_end = globals.get_angle_to_point(r[0][0], r[0][1], cross_section[1][0], cross_section[1][1])
            if abs(angle_to_end - angle_to_start) < 180:
                return min(angle_to_start, angle_to_end) <= self.angle <= max(angle_to_start, angle_to_end)
            else:
                return not min(angle_to_start, angle_to_end) <= self.angle <= max(angle_to_start, angle_to_end)
            
            
    def collide_mask(self, mask: pygame.Mask, mask_coords):
        outline = mask.outline()
        angles = []

        for r in self.rays:
            for i in outline:
                angles.append(globals.get_angle_to_point(r[0][0], r[0][1], mask_coords[0] + i[0], mask_coords[1] + i[1]))
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
            cross_section = ((outline[min_index][0] + mask_coords[0], outline[min_index][1] + mask_coords[1]),
                    ((outline[max_index][0] + mask_coords[0], outline[max_index][1] + mask_coords[1])))

            angle_to_start = globals.get_angle_to_point(r[0][0], r[0][1], cross_section[0][0],
                                                        cross_section[0][1])
            angle_to_end = globals.get_angle_to_point(r[0][0], r[0][1], cross_section[1][0],
                                                      cross_section[1][1])
            if abs(angle_to_end - angle_to_start) < 180:
                return min(angle_to_start, angle_to_end) <= self.angle <= max(angle_to_start, angle_to_end)
            else:
                return not min(angle_to_start, angle_to_end) <= self.angle <= max(angle_to_start, angle_to_end)
