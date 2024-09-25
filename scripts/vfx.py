import pygame
from .utils import advance

""" self.color = (0, 255, 0)
self.size = (36, 18)
self.arc_width = 13
self.width_decay = 50
self.angle = random.randint(0, 360) """

class Arc:
    def __init__(self, game, pos, size, width, width_decay, angle, color=(255, 255, 255)):
        self.game = game
        self.pos = pos
        self.size = size
        self.width = width
        self.width_decay = width_decay
        self.angle = angle
        self.color = color

        self.swipe_surf = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.ellipse(self.swipe_surf, self.color, self.swipe_surf.get_rect())
        pygame.draw.ellipse(self.swipe_surf, self.color, pygame.Rect(self.swipe_surf.get_rect()[0] - 4, self.swipe_surf.get_rect()[1], self.swipe_surf.get_rect()[2], self.swipe_surf.get_rect()[3]))
        self.swipe_surf.set_colorkey((0, 0, 0))

        self.alive = True
    
    def update(self, dt):
        self.width -= dt * self.width_decay
        if self.width <= 0:
            return False
        return True

    def render(self, offset=(0, 0)):
        mask_size = self.size
        mask_surf = pygame.Surface(mask_size, pygame.SRCALPHA)
        pygame.draw.ellipse(mask_surf, (0, 0, 0), mask_surf.get_rect())
        self.swipe_surf.blit(mask_surf, (-self.width, (self.swipe_surf.height // 2) - (mask_surf.height) // 2))
        
        img = pygame.transform.scale(self.swipe_surf, (self.swipe_surf.width * self.game.window.scale_ratio, self.swipe_surf.height * self.game.window.scale_ratio))
        img = pygame.transform.rotate(img, self.angle)
        self.game.renderer.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))


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