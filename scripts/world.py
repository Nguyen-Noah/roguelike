import pygame, math, json
from .config import config
from .tilemap import Tilemap
from .players.test_player import Player
from .camera import Camera

class World:
    def __init__(self, game):
        self.game = game

        self.player = Player(game, 'player')

        self.tilemap = Tilemap(game)
        self.load('data/maps/map.json')

        self.camera = Camera(game)
        self.camera.set_tracked_entity(self.player)

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    def update(self):
        dt = self.game.window.dt

        self.camera.update()
        self.player.update(dt)

        self.render(offset=self.camera.int_pos)
        self.player.render(offset=self.camera.int_pos)

    def render(self, offset=(0, 0)):
        surf = self.game.window.display
        for tile in self.offgrid_tiles:
            self.game.renderer.blit(self.game.assets.temp[tile['type']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        for x in range(offset[0] // (self.tile_size * self.game.window.scale_ratio), (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // (self.tile_size * self.game.window.scale_ratio), (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    self.game.renderer.blit(self.game.assets.temp[tile['type']], 
                                            (tile['pos'][0] * (self.tile_size * self.game.window.scale_ratio) - offset[0], 
                                             tile['pos'][1] * (self.tile_size * self.game.window.scale_ratio) - offset[1])
                                            )
