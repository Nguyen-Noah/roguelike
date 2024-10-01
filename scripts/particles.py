import random
from .utils import normalize

PARTICLE_FUNCS = {'behave': {}, 'init': {}}
ANIMATION_CACHE = {}

def particle_init(argument):
    def decorator(func):
        PARTICLE_FUNCS['init'][argument] = func
        return func
    return decorator

def particle_behavior(argument):
    def decorator(func):
        PARTICLE_FUNCS['behave'][argument] = func
        return func
    return decorator

@particle_init('idle')
def idle_init(self):
    pass

@particle_behavior('idle')
def idle_behave(self, dt):
    pass

@particle_init('physics_example')
def physics_ex_init(self):
    self.acceleration[1] = 600
    self.terminal[1] = 300
    self.velocity_normilization[0] = 50

@particle_behavior('physics_example')
def physics_ex_behave(self, dt):
    pass

class Particle:
    def __init__(self, game, pos, particle_type, velocity=(0, 0), decay_rate=1.0, advance=0.0, behavior='idle', colors=None, z=0, physics_source=None):
        self.game = game
        self.pos = list(pos)
        self.type = particle_type
        self.velocity = list(velocity)
        self.acceleration = [0, 0]
        self.terminal = [99999, 99999]
        self.velocity_normalization = [0, 0]
        self.next_movement = [0, 0]
        self.bounce = 0.5
        self.unique = random.random() * 1000
        self.decay_rate = decay_rate
        self.advance = advance
        self.behavior= behavior
        self.colors = colors
        self.z = z
        self.physics_source = physics_source

        self.animation = self.game.entity_db[self.type].animations[self.type].copy()
        self.animations.config['loop'] = False

        if colors:
            colors_id = (self.type, tuple((tuple(k), tuple(v)) for k, v in colors.items()))
            if colors_id in ANIMATION_CACHE:
                self.animation = ANIMATION_CACHE[colors_id].copy()
            else:
                self.animation = self.animation.hard_copy()
                self.animation.palette_swap(colors)
                ANIMATION_CACHE[colors_id] = self.animation
        self.animation.update(advance)
        PARTICLE_FUNCS['init'][behavior](self)

    def update(self, dt):
        self.animation.update(dt * self.decay_rate)

        PARTICLE_FUNCS['behave'][self.behavior](self, dt)

        self.next_movement[0] += self.velocity[0] * dt
        self.next_movement[1] += self.velocity[1] * dt

        self.pos += self.next_movement[0]
        if self.physics_source:
            collision = self.physics_source.physics_gridtile(self.pos)
            if collision and (collision.physics_type == 'solid'):
                self.velocity[0] *= -self.bounce
                if self.next_movement[0] > 0:
                    self.pos[0] = collision.rect.left
                if self.next_movement[0] < 0:
                    self.pos[0] = collision.rect.right
        self.pos[1] += self.next_movement[1]
        if self.physics_source:
            collision = self.physics_source.physics_gridtile(self.pos)
            if collision and (collision.physics_type == 'solid'):
                self.velocity[1] *= -self.bounce
                if self.next_movement[1] > 0:
                    self.pos[1] = collision.rect.top
                if self.next_movement[1] < 0:
                    self.pos[1] = collision.rect.bottom

        self.velocity[0] += self.acceleration[0] * dt
        self.velocity[1] += self.acceleration[1] * dt
        self.velocity[0] = normalize(self.velocity[0], self.velocity_normalization[0] * dt)
        self.velocity[1] = normalize(self.velocity[1], self.velocity_normalization[1] * dt)
        self.velocity[0] = max(-self.terminal[0], min(self.terminal[0], self.velocity[0]))
        self.velocity[0] = max(-self.terminal[1], min(self.terminal[1], self.velocity[1]))
        self.next_movement = [0, 0]
        return self.animation.finished
    
    def renderz(self, group='default', offset=(0, 0)):
        img = self.animation.img
        self.game.renderer.blit(img, (self.pos[0] - offset[0] - (img.width // 2), self.pos[1] - offset[1] - (img.height // 2)))