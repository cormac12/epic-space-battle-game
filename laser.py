import math

class Laser:
    def __init__(self, origin, angle, width, color, damage, parent):
        self.origin = origin
        self.angle = angle
        self.width = width
        self.color = color
        self.damage = damage
        self.parent = parent
        self.is_on = False
        self.vectors = []
        self.vectors.append((self.origin, self.angle))
        self.vectors.append(((self.origin[0] - math.cos(math.radians(angle)) * self.width/2,
                              self.origin[1] - math.sin(math.radians(angle)) * self.width/2), self.angle))
        self.vectors.append(((self.origin[0] + math.cos(math.radians(angle)) * self.width/2,
                              self.origin[1] + math.sin(math.radians(angle)) * self.width/2), self.angle))
    
    
    def set_angle(self, angle):
        self.angle = angle
        self.vectors = []
        self.vectors.append((self.origin, self.angle))
        self.vectors.append(((self.origin[0] - math.cos(math.radians(angle)) * self.width/2,
                              self.origin[1] - math.sin(math.radians(angle)) * self.width/2), self.angle))
        self.vectors.append(((self.origin[0] + math.cos(math.radians(angle)) * self.width/2,
                              self.origin[1] + math.sin(math.radians(angle)) * self.width/2), self.angle))

    def set_pos(self, x, y):
        self.origin = (x, y)
        self.vectors = []
        self.vectors.append((self.origin, self.angle))
        self.vectors.append(((self.origin[0] - math.cos(math.radians(self.angle)) * self.width/2,
                              self.origin[1] - math.sin(math.radians(self.angle)) * self.width/2), self.angle))
        self.vectors.append(((self.origin[0] + math.cos(math.radians(self.angle)) * self.width/2,
                              self.origin[1] + math.sin(math.radians(self.angle)) * self.width/2), self.angle))

