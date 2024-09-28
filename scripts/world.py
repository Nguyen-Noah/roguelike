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

        self.render(offset=self.game.camera.int_pos)
        self.vfx.render(offset=self.game.camera.int_pos)

    def render(self, offset=(0, 0)):
        self.tilemap.render()
