import pygame, time

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
        self.combo_limit = 0

        self.invisible = 0

    def reset_combo(self):
        self.combo = 0
