from .entity import Entity
from .utils import collision_list
from .config import config

class RigidBody(Entity):
    def __init__(self, game, type, pos, mass=1.0, friction=0.05):
        super().__init__(game, type, pos)
        self.data = config['player'][type]
        self.velocity = [0, 0]
        self.acceleration = [0, 0]
        self.mass = mass
        self.friction = friction
        self.collide_directions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.frame_dir = [0, 0]

    def apply_force(self, force):
        self.acceleration += force / self.mass

    def handle_turn(self):
        if self.frame_dir[0] == 1 and self.flip[0]:
            self.flip[0] = False
        elif self.frame_dir[0] == -1 and not self.flip[0]:
            self.flip[0] = True

    def handle_run(self, dt):
        target_speed = (self.frame_dir[0] * self.data['max_run_speed'], self.frame_dir[1] * self.data['max_run_speed'])

        if abs(target_speed[0]) > 0.01 or abs(target_speed[1]) > 0.01:
            accel_rate = self.data['run_accel_rate']
        else:
            accel_rate = self.data['run_deccel_rate']

        speed_diff = (target_speed[0] - self.velocity[0], target_speed[1] - self.velocity[1])

        movement = (speed_diff[0] * accel_rate, speed_diff[1] * accel_rate)

        self.velocity[0] += movement[0] * dt
        self.velocity[1] += movement[1] * dt
    
    def physics_update(self, movement):
        #neighbors = self.game.world.tilemap.solids_around(self.center)
        neighbors = []

        self.pos[0] += movement[0]
        init_rect = self.rect
        rect = self.rect
        for tile in neighbors:
            if tile.rect.colliderect(self.rect):
                if movement[0] > 0:
                    rect.right = tile.rect.left
                if movement[0] < 0:
                    rect.left = tile.rect.right
        if init_rect.x != rect.x:
            self.pos[0] = rect.x

        self.pos[1] += movement[1]
        init_rect = self.rect
        rect = self.rect
        for tile in neighbors:
            if tile.rect.colliderect(self.rect):
                if movement[1] > 0:
                    rect.bottom = tile.rect.top
                if movement[1] < 0:
                    rect.top = tile.rect.bottom
        if init_rect.y != rect.y:
            self.pos[1] = rect.y