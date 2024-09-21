from .entity import Entity
from .utils import collision_list

class RigidBody(Entity):
    def __init__(self, game, type, pos, mass=1.0, friction=0.05):
        super().__init__(game, type, pos)
        self.velocity = [0, 0]
        self.acceleration = [0, 0]
        self.mass = mass
        self.friction = friction
        self.collide_directions = {'up': False, 'down': False, 'right': False, 'left': False}

        # state parameters
        self._is_facing_right = True

    @property
    def is_facing_right(self):
        return self._is_facing_right

    def apply_force(self, force):
        self.acceleration += force / self.mass

    def move(self, motion, tiles):
        self.pos[0] += motion[0]
        hit_list = collision_list(self.rect, tiles)
        temp_rect = self.rect
        directions = {k : False for k in ['top', 'left', 'right', 'bottom']}
        for tile in hit_list:
            if motion[0] > 0:
                temp_rect.right = tile.left
                self.pos[0] = temp_rect.x
                directions['right'] = True
            if motion[0] < 0:
                temp_rect.left = tile.right
                self.pos[0] = temp_rect.x
                directions['left'] = True
            if self.centered:
                self.pos[0] += self.size[0] // 2
        self.pos[1] += motion[1]
        hit_list = collision_list(self.rect, tiles)
        temp_rect = self.rect
        for tile in hit_list:
            if motion[1] > 0:
                temp_rect.bottom = tile.top
                self.pos[1] = temp_rect.y
                directions['bottom'] = True
            if motion[1] < 0:
                temp_rect.top = tile.bottom
                self.pos[1] = temp_rect.y
                directions['top'] = True
            if self.centered:
                self.pos[1] += self.size[1] // 2
        return directions
    
    def physics_update(self, movement):
        neighbors = self.game.world.tilemap.solids_around(self.center)

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