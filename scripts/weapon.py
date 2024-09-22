import pygame

class Weapon:
    def __init__(self, game, weapon_type, owner):
        self.game = game
        self.type = weapon_type
        self.owner = owner
        