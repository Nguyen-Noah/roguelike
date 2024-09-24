import pygame, time
from .config import config

WEAPON_NAMES = {
    'sword': 'Sword'
}

class Weapon:
    def __init__(self, game, weapon_type, owner):
        self.game = game
        self.type = weapon_type
        self.owner = owner
        self.rotation = 0

        self.combo = 0
        self.combo_limit = config['weapons'][self.type]['combo']
        self.attack_rate = config['weapons'][self.type]['attack_rate']
        self.last_attack = time.time()
        self.attack_timer = 0

        self.invisible = 0

    def reset_combo(self):
        self.combo = 0

    def reset_attack(self):
        self.attacking = False

    def attack(self):
        self.attacking = True
        self.combo += 1

    def attempt_attack(self):
        if self.combo == self.combo_limit:
            self.reset_combo()
        else:
            if (time.time() - self.last_attack > self.attack_rate) and not self.attacking:
                self.last_attack = time.time()
                self.attack()
                return True
            
        return False
    
    def update(self, dt):
        if self.attacking:
            self.attack_timer += dt
            if self.attack_timer > self.attack_rate:
                self.reset_attack()
                self.attack_timer = 0