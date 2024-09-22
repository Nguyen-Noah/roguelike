import pygame, math
from ..hair import Hair
from ..rigidbody import RigidBody
from ..animation import Animation

class Player(RigidBody):
    def __init__(self, game, type):
        super().__init__(game, type, [40, 40])
        self.game = game
        self.hair_gravity = None
        self.hair = Hair(game, self)

    def update(self, dt):
        super().update(dt)

        movement = self.velocity.copy()
        if not self.dead:
            self.handle_run(dt)

            self.frame_dir = [0, 0]
            if self.game.input.holding('right') and not self.game.input.holding('left'):
                self.frame_dir[0] = 1
            elif self.game.input.holding('left') and not self.game.input.holding('right'):
                self.frame_dir[0] = -1
            else:
                self.frame_dir[0] = 0

            # Vertical movement (up and down)
            if self.game.input.holding('down') and not self.game.input.holding('up'):
                self.frame_dir[1] = 1
            elif self.game.input.holding('up') and not self.game.input.holding('down'):
                self.frame_dir[1] = -1
            else:
                self.frame_dir[1] = 0

            # normalize diagonal movement
            if (movement[0] and movement[1]):
                movement[0] /= math.sqrt(2)
                movement[1] /= math.sqrt(2)

        self.physics_update(movement)

        if any(self.frame_dir):
            self.set_action('walk')
        else:
            self.set_action('idle')

        self.handle_turn()
        self.hair_gravity(-.025)
        self.hair.update(dt)

    def render(self, offset=(0, 0)):
        self.game.renderer.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def debug(self):
        print(self.action)
        print(self.flip)