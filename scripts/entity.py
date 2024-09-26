import pygame

ANIMATIONS = 'animations'
OFFSET_N4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

class Entity:
    def __init__(self, game, type, pos, z=0):
        self.game = game
        self.type = type
        self.pos = pos
        self.z = z
        self.config = self.game.entity_db[self.type].config
        self.assets = self.game.entity_db[self.type].assets
        self.animations = self.game.entity_db[self.type].animations
        self.action = self.config['default']
        self.source = ANIMATIONS if self.action in self.animations else 'images'
        self.animation = None if self.source != ANIMATIONS else self.animations[self.action].copy()
        self.size = self.config['size']
        self.dead = False

        # rendering options
        self.opacity = 255
        self.scale = [self.game.window.scale_ratio, self.game.window.scale_ratio]
        self.rotation = 0
        self.flip = [False, False]
        self.visible = True

        self.tweaked = False

        self.outline = None

    @property
    def center(self):
        return self.rect.center
    
    @property
    def rect(self):
        return pygame.Rect(*self.pos, *self.size)
    
    @property
    def local_offset(self):
        img_offset = self.config[self.source][self.action]['offset']
        entity_offset = self.config['offset']
        return (img_offset[0] + entity_offset[0], img_offset[1] + entity_offset[1])
    
    @property
    def raw_img(self):
        if self.source == ANIMATIONS:
            return self.animation.img
        return self.assets[self.action]
    
    @property
    def img(self):
        raw_img = self.raw_img
        img = raw_img
        base_dimensions = img.get_size()
        if self.scale != [1, 1]:
            img = pygame.transform.scale(img, (int(self.scale[0] * base_dimensions[0]), int(self.scale[1] * base_dimensions[1])))
            self.tweaked = True
        if any(self.flip):
            img = pygame.transform.flip(img, self.flip[0], self.flip[1])
        if self.rotation:
            img = pygame.transform.rotate(img, self.rotation)
            self.tweaked = True
        if self.opacity != 255:
            if img == raw_img:
                img = img.copy()
            img.set_alpha(self.opacity)
        return img
    
    def set_action(self, action, force=False):
        if not force and (self.action == action):
            return
        self.action = action
        self.source = ANIMATIONS if self.action in self.animations else 'images'
        if self.source == ANIMATIONS:
            self.animation = self.animations[self.action].copy()

    def topleft(self, offset=(0, 0)):
        img_size = self.img.get_size()
        if (not self.tweaked) or self.config['centered']:
            center_offset = (img_size[0] // 2, img_size[1] // 2) if self.config['centered'] else (0, 0)
            return (self.pos[0] - offset[0] + self.local_offset[0] - center_offset[0], self.pos[1] - offset[1] + self.local_offset[1] - center_offset[1])
        else:
            raw_img_size = self.raw_img.get_size()
            size_diff = (img_size[0] - raw_img_size[0], img_size[1] - raw_img_size[1])
            dynamic_offset = [-size_diff[0] // 2, -size_diff[1] // 2]
            return (self.pos[0] - offset[0] + self.local_offset[0] + dynamic_offset[0], self.pos[1] - offset[1] + self.local_offset[1] + dynamic_offset[1])
        
    def center_self(self):
        img_size = self.img.get_size()
        raw_img_size = self.raw_img.get_size()
        size_diff = (img_size[0] - raw_img_size[0], img_size[1] - raw_img_size[1])
        dynamic_offset = [-size_diff[0] // 2, -size_diff[1] // 2]
        return (dynamic_offset[0] + self.local_offset[0], dynamic_offset[1] + self.local_offset[1])

    def update(self, dt):
        if self.source == ANIMATIONS:
            self.animation.update(dt)
    
    def render(self, surf, offset=(0, 0)):
        if self.visible:
            surf.blit(self.img, self.topleft(offset))

    def renderz(self, offset=(0, 0), group='default'):
        if self.visible:
            dynamic_offset = self.center_self()
            if self.outline:
                silhouette = pygame.mask.from_surface(self.img).to_surface(setcolor=self.outline, unsetcolor=(0, 0, 0, 0))
                silhouette.set_alpha(self.opacity)
                for offset in OFFSET_N4:
                    self.game.renderer.blit(silhouette, (self.pos[0] + dynamic_offset[0] - offset[0], self.pos[1] + dynamic_offset[1] - offset[1]), z=self.z - 0.000001, group=group)
            self.game.renderer.blit(self.img, (self.pos[0] + dynamic_offset[0] - offset[0], self.pos[1] + dynamic_offset[1] - offset[1]), z=self.z, group=group)
            if self.weapon:
                self.weapon.render((self.center[0] + dynamic_offset[0], self.center[1] + dynamic_offset[1]), offset=offset)