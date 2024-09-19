import pygame
from ..hair import Hair

class Player:
    def __init__(self, game):
        self.game = game
        self.hair_gravity = None
        self.hair = Hair(game, self)
        self.position = (0, 0)

    def update(self, dt):
        self.position = pygame.mouse.get_pos()
        self.hair_gravity(-.025)
        self.hair.update(dt)