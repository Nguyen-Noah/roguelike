from .entity import Entity

class RigidBody(Entity):
    def __init__(self, game, type, pos, mass=1.0, friction=0.05):
        super().__init__(game, type, pos)
        self.velocity = (0, 0)
        self.acceleration = (0, 0)
        self.mass = mass
        self.friction = friction

        # state parameters
        self._is_facing_right = True

    def apply_force(self, force):
        self.acceleration += force / self.mass

    @property
    def is_facing_right(self):
        return self._is_facing_right

    @property
    def last_on_ground_time(self):
        return self._last_on_ground_time
