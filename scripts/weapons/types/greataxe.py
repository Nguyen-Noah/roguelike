import pygame, math
from ...weapon import Weapon

def lerp(a, b, t):
    return a + (b - a) * t

class Greataxe(Weapon):
    def __init__(self, game, weapon_type, owner):
        super().__init__(game, weapon_type, owner)
        self.offset = (-12, -10)
        self.swing_speed = 20

        self.swing = -1
        self.swing_angle = 0
        self.target = 0
        self.weapon_angle = 20
        self.swinging = False

        self.static_angle = True

    def attempt_attack(self):
        if super().attempt_attack():
            self.swing *= -1

    def update(self, dt):
        super().update(dt)
        if self.attacking:
            pass

    def render(self, loc, offset=(0, 0)):
        self.invisible = 0
        img = self.game.assets.weapons[self.type].copy()
        if not self.invisible:
            flip = self.owner.flip[0]
            img = pygame.transform.flip(img, flip, False)

            sword_dist = 25
            render_pos = (loc[0] - (img.width // 2) - offset[0] + self.offset[0], loc[1] - (img.get_height() // 2) - offset[1] + self.offset[1])
            self.game.renderer.blit(img, render_pos)
