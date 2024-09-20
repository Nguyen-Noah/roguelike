import pygame
from ..hair import Hair
from ..rigidbody import RigidBody

class Player(RigidBody):
    def __init__(self, game):
        super().__init__(game, 'player', (40, 40))
        self.game = game
        self.hair_gravity = None
        self.hair = Hair(game, self)

    def update(self, dt):
        self.pos = self.game.input.mouse_pos
        self.hair_gravity(-.025)
        self.hair.update(dt)