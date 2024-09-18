import pygame

class Renderer:
    def __init__(self, game):
        self.game = game

    def cycle(self):
        pygame.draw.circle(self.game.window.display, 'red', (10, 10), 5)