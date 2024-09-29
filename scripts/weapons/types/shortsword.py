import pygame, math
from ...weapon import Weapon

def lerp(a, b, t):
    return a + (b - a) * t

class Shortsword(Weapon):
    def __init__(self, game, weapon_type, owner):
        super().__init__(game, weapon_type, owner)
        self.swing_speed = 20

        self.swing = -1
        self.swing_angle = 0
        self.target = 0
        self.weapon_angle = -134
        self.swinging = False

    def process_swing(self, dt):
        self.swing_angle = lerp(self.swing_angle, self.swing * 135, dt * self.swing_speed)

        t = 255 if self.swing == 1 else -45
        self.target = lerp(self.target, t, dt * self.swing_speed)

        if abs(t - self.target) < 5:
            self.swinging = False

        self.weapon_angle = self.swing_angle

    def attempt_attack(self):
        if super().attempt_attack():
            self.swing *= -1

    def update(self, dt):
        super().update(dt)
        if self.attacking:
            self.process_swing(dt)

    def render(self, loc, offset=(0, 0)):
        self.invisible = 0
        img = self.game.assets.weapons[self.type].copy()
        if not self.invisible:
            if self.swing == -1:
                img = pygame.transform.flip(img, False, False)
            else:
                img = pygame.transform.flip(img, False, True)
            if (self.angle % 360 < 270) and (self.angle % 360 > 90):
                angle_offset = -20
            else:
                angle_offset = 20

            img = pygame.transform.rotate(img, -self.angle + angle_offset - self.weapon_angle)
            sword_dist = 25
            render_pos = (loc[0] - (img.width // 2) + (math.cos(math.radians(self.angle + self.weapon_angle)) * sword_dist) - offset[0], loc[1] - (img.get_height() // 2) - (math.sin(math.radians(-self.angle - self.weapon_angle)) * sword_dist) - offset[1])
            self.game.renderer.blit(img, render_pos)

        """ img_rect = img.get_rect()
        pygame.draw.rect(self.game.window.display, 'red', (img_rect[0] + render_pos[0], img_rect[1] + render_pos[1], img_rect[2], img_rect[3]), 4) """

    def debug(self):
        print('attacking: ', self.attacking)
        print('')