import math

def lerp(v1, v2, t):
    #return vec2(v1.x + t * (v2.x - v1.x), v1.y + t * (v2.y - v1.y))
    return [v1[0] + t * (v2[0] - v1[0]), v1[1] + t * (v2[1] - v1[1])]

def magnitude(vec):
    return math.sqrt(vec[0] ** 2 + vec[1] ** 2)

def normalize(vec):
    mag = magnitude(vec)
    if mag > 0:
        return (vec[0] / mag, vec[1] / mag)
    return (0, 0)
