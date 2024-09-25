import math, pygame
from .utils import advance

class Arc:
    def __init__(self, game, pos, radius, spacing, start_angle, speed, curve_rate, scale, start=1, end=1, duration=30, color=(255, 255, 255), fade=0.3, arc_stretch=0, width_decay=50, decay=['up', 60], angle_width=0.2, motion=0):
        self.game = game
        self.pos = list(pos)
        self.radius = radius
        self.spacing = spacing
        self.start_angle = start_angle
        self.speed = speed
        self.curve_rate = curve_rate
        self.scale = scale
        self.start = start
        self.end = end
        self.duration = duration
        self.color = color
        self.fade = fade
        self.arc_stretch = arc_stretch
        self.width_decay = width_decay
        self.decay = decay
        self.angle_width = angle_width
        self.motion = motion

        self.time = 0
        self.alive = True
        self.width = 1.2

    def get_angle_point(self, base_point, t, curve_rate):
        p = advance(base_point.copy(), self.start_angle + (0.5 - t) * math.pi * 4 * self.angle_width, self.radius)
        advance(p, self.start_angle, (0.5 ** 2 - abs(0.5 - t) ** 2) * self.radius * curve_rate)
        if self.arc_stretch != 0:
            advance(p, self.start_angle + math.pi / 2, (0.5 - t) * self.arc_stretch * self.scale)
        return p
    
    def calculate_points(self, start, end, curve_rate):
        base_point = advance([0, 0], self.start_angle, self.spacing)
        point_count = 20
        arc_points = [self.get_angle_point(base_point, start + (i / point_count) * (end - start), curve_rate) for i in range(point_count + 1)]
        arc_points = [[p[0] * self.scale, p[1] * self.scale]for p in arc_points]
        return arc_points
    
    def create_mask(self):
        start = self.start
        end = self.end
        points = self.calculate_points(start, end, self.curve_rate + self.time / 12) + self.calculate_points(start, end, (self.curve_rate + self.time / 12) * self.width)[::-1]
        points = [[p[0] + self.pos[0], p[1] + self.pos[1]] for p in points]
        points_x = [p[0] for p in points]
        points_y = [p[1] for p in points]
        min_x = min(points_x)
        min_y = min(points_y)
        mask_surf = pygame.Surface((max(points_x) - min_x + 1, max(points_y) - min_y + 1))
        points = [[p[0] - min_x, p[1] - min_y] for p in points]
        pygame.draw.polygon(mask_surf, (255, 255, 255), points)
        mask_surf.set_colorkey((0, 0, 0))
        return pygame.mask.from_surface(mask_surf), (min_x, min_y)
    
    def update(self, dt):
        self.time += self.speed * dt
        if self.decay[0] == 'up':
            self.start -= self.start / 20 * dt * self.decay[1]
        elif self.decay[0] == 'down':
            self.end += (1 - self.end) / 20 * dt * self.decay[1]
        self.width += (1 - self.width) / 4 * dt * self.width_decay
        self.spacing += self.motion * dt
        if self.time > self.duration:
            self.alive = False

        return self.alive
    
    def render(self, surf, offset=(0, 0)):
        if self.time > 0:
            start = self.start
            end = self.end
            points = self.calculate_points(start, end, self.curve_rate + self.time / 12) + self.calculate_points(start, end, (self.curve_rate + self.time / 12) * self.width)[::-1]
            points = [[p[0] - offset[0] + self.pos[0], p[1] - offset[1] + self.pos[1]] for p in points]
            c = [int(self.color[i] - self.color[i] * self.fade * self.time / self.duration) for i in range(3)]
            pygame.draw.polygon(surf, c, points)



VFX_TYPES = {
    'arc': Arc
}

class VFX:
    def __init__(self, game):
        self.game = game
        self.front_effects = []
        self.back_effects = []

    def spawn_vfx(self, effect_type, *args, layer='front', **kwargs):
        if layer == 'front':
            self.front_effects.append(VFX_TYPES[effect_type](self.game, *args, **kwargs))
        if layer == 'back':
            self.back_effects.append(VFX_TYPES[effect_type](self.game, *args, **kwargs))

    def update(self, dt):
        for group in [self.front_effects, self.back_effects]:
            for i, effect in enumerate(group):
                alive = effect.update(dt)
                if not alive:
                    group.pop(i)

    def render(self, surf, offset=(0, 0)):
        for effect in self.front_effects:
            effect.render(surf, offset)