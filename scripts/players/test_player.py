import pygame, math
from ..hair import Hair
from ..rigidbody import RigidBody

class Player(RigidBody):
    def __init__(self, game):
        super().__init__(game, 'player', (40, 40))
        self.game = game
        self.hair_gravity = None
        self.hair = Hair(game, self)


        self.speed = 1

    def update(self, dt):
        movement = [0, 0]
        if not self.dead:
            if self.game.input.holding('right'):
                movement[0] += self.speed * dt
            if self.game.input.holding('left'):
                movement[0] -= self.speed * dt
            if self.game.input.holding('down'):
                movement[1] += self.speed * dt
            if self.game.input.holding('up'):
                movement[1] -= self.speed * dt

            # normalize diagonal movement
            if (movement[0] and movement[1]):
                movement[0] /= math.sqrt(2)
                movement[1] /= math.sqrt(2)

        self.physics_update(movement)

        self.hair_gravity(-.025)
        self.hair.update(dt)
        self.render()

    def render(self):
        self.game.renderer.blit(self.img, self.pos)