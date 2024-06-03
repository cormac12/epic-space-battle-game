import math

class Laser:
    def __init__(self, origin, direction, width, color, parent):
        self.origin = origin
        self.direction = direction
        self.width = width
        self.color = color
        self.parent = parent
        self.vectors = []
        self.vectors.append((self.origin, self.direction))
        self.vectors.append(((self.origin[0] - math.cos(math.radians(direction)) * self.width/2,
                              self.origin[1] - math.sin(math.radians(direction)) * self.width/2), self.direction))
        self.vectors.append(((self.origin[0] + math.cos(math.radians(direction)) * self.width/2,
                              self.origin[1] + math.sin(math.radians(direction)) * self.width/2), self.direction))

