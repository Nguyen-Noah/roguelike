import pygame, math
from ..rigidbody import RigidBody
from ..animation import Animation
from ..weapons.wood_sword import WoodSword
from ..weapons.iron_axe import IronAxe

class Player(RigidBody):
    def __init__(self, game, type):
        super().__init__(game, type, [40, 40])
        self.game = game
        self.hair_gravity = None
        self.weapon = WoodSword(game, 'wood_sword', self)

    def update(self, dt):
        super().update(dt)

        movement = self.velocity.copy()
        if not self.dead:
            # -------------------------------- MOVEMENT
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

            # -------------------------------- MOUSE ANGLE
            angle = math.atan2(self.game.input.mouse.pos[1] - self.center[1] + self.game.camera.render_offset[1], self.game.input.mouse.pos[0] - self.center[0] + self.game.camera.render_offset[0])
            self.aim_angle = angle
            if self.weapon:
                self.weapon.angle = math.degrees(angle)

            # --------------------------------- TURN
            if (math.degrees(self.aim_angle) % 360 < 270) and (math.degrees(self.aim_angle) % 360 > 90):
                self.flip[0] = True
            else:
                self.flip[0] = False

            if self.game.input.holding('attack'):
                self.weapon.attempt_attack()

        self.physics_update(movement)

        if any(self.frame_dir):
            self.set_action('walk')
        else:
            self.set_action('idle')

        self.weapon.update(dt)

    def render(self, offset=(0, 0)):
        self.game.renderer.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        self.weapon.render(self.center, offset)

    def debug(self):
        print(self.action)
        print(self.flip)