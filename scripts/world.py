import pygame, math, json
from .config import config
from .tilemap import Tilemap
from .players.test_player import Player

class World:
    def __init__(self, game):
        self.game = game

        self.load('data/maps/map.json')
        self.player = Player(self.game)

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        print(map_data.keys())

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    def update(self, offset=(0, 0)):

        # rendering
        surf = self.game.window.display
        for tile in self.offgrid_tiles:
            self.game.renderer.blit(self.game.assets.temp[tile['type']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    self.game.renderer.blit(self.game.assets.temp[tile['type']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

        self.player.update(1/60)