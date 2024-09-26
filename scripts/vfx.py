import pygame, math
from .utils import ease_out_cubic

class Arc:
    def __init__(self, game, pos, size, width, width_decay, angle, distance=0, color=(255, 255, 255)):
        self.game = game
        self.pos = pos
        self.size = size
        self.width = width
        self.width_decay = width_decay
        self.angle = angle
        self.distance = distance
        self.color = color

        self.gen_base()

        self.completion = 0
        self.blit_pos = (math.cos(math.radians(self.angle)) * self.distance, math.sin(math.radians(self.angle)) * self.distance)
    
    @property
    def mask(self):
        return pygame.mask.from_surface(self.swipe_surf)

    def gen_base(self):
        self.swipe_surf = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.ellipse(self.swipe_surf, self.color, self.swipe_surf.get_rect())
        pygame.draw.ellipse(self.swipe_surf, self.color, pygame.Rect(self.swipe_surf.get_rect()[0] - 4, self.swipe_surf.get_rect()[1], self.swipe_surf.get_rect()[2], self.swipe_surf.get_rect()[3]))
        self.swipe_surf.set_colorkey((0, 0, 0))

        self.mask_surf = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.ellipse(self.mask_surf, (0, 0, 0), self.mask_surf.get_rect())

    def update(self, dt):
        self.completion += self.width_decay * dt
        self.completion = min(self.width, self.completion)
        value = 1 - ease_out_cubic(self.completion / self.width)

        if value <= 0:
            return False
        self.swipe_surf.blit(self.mask_surf, (-self.width * value, (self.swipe_surf.height // 2) - (self.mask_surf.height) // 2))
        return True

    def render(self, offset=(0, 0)):
        img = pygame.transform.scale(self.swipe_surf, (self.swipe_surf.width * self.game.window.scale_ratio, self.swipe_surf.height * self.game.window.scale_ratio))
        img = pygame.transform.rotate(img, self.angle)
        self.game.renderer.blit(img, (self.pos[0] - (img.width // 2) + self.blit_pos[0] - offset[0], self.pos[1] - (img.height // 2) - self.blit_pos[1] - offset[1]))

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

    def render(self, offset=(0, 0)):
        for effect in self.front_effects:
            effect.render(offset)