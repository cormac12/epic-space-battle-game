import math


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

globals_dict = {}