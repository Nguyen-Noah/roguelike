import pygame, math, json, random
from .config import config
from .tilemap import Tilemap
from .players.test_player import Player
from .vfx import VFX

class World:
    def __init__(self, game):
        self.game = game
        self.vfx = VFX(game)
        self.player = Player(game, 'player')
        self.game.entity_groups.add(self.player, 'entities')
        self.tilemap = Tilemap(game)
        self.game.camera.set_tracked_entity(self.player)

    def update(self):
        dt = self.game.window.dt

        self.vfx.update(dt)

        self.render(offset=self.game.camera)
        self.vfx.render(offset=self.game.camera)

        """ if self.game.input.holding('attack'):
            for i in range(10):
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                self.vfx.spawn_vfx('spark', list(self.game.input.mouse.pos), random.random(), random.random() * 9, random.random() * 40, color=color, height=12, width=0.8) """

    def render(self, offset=(0, 0)):
        pass
        #self.tilemap.render()
