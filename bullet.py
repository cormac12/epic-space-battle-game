class Bullet:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update_coords(self):
        self.x += self.vx
        self.y += self.vy
