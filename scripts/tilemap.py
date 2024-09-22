import pygame, json

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'temp'}
AUTOTILE_TYPES = {'temp'}
TILES_AROUND = [(0, 0), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 1), (1, 1), (-1, 1)]


class Tile:
    def __init__(self, group, tile_id=(0, 0), pos=(0, 0), layer=0, custom_data=''):
        self.group = group
        self.tile_id = tile_id

    def change_id(self, tile_id):
        self.tile_id = tile_id
        self.img

class Tilemap:
    def __init__(self, game, tile_size=16, dimensions=(16, 16)):
        self.game = game
        self.tile_size = tile_size
        self.dimensions = tuple(dimensions)
        self.grid_tiles = {}
        self.offgrid_tiles = []

    def save(self, path):
        output = {
            'tile_size': self.tile_size,
            'grid_tiles': {},
            'offgrid_tiles': self.offgrid_tiles,
            'dimensions': self.dimensions
            }
        for loc in self.grid_tiles:
            output['grid_tiles'][loc] = {}
            for layer in self.grid_tiles[loc]:
                output['grid_tiles'][loc][layer] = self.grid_tiles[loc][layer].export()
        

    def load_map(self):
        self.clear()


    def clear(self):
        self.floor = {}
        self.walls = {}
        self.solids = {}
        self.gaps = {}

    # takes pixel positions, not grid position
    def get_tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos.x // self.tile_size), int(pos.y // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = f'{str(tile_loc[0] + offset[0])};{str(tile_loc[1] + offset[1])}'
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        
        return tiles

    def solids_around(self, pos_px, include_gaps=True):
        pos = (int(pos_px[0] // self.tile_size), int(pos_px[1] // self.tile_size))
        solids = []
        for offset in TILES_AROUND:
            check = (pos[0] + offset[0], pos[1] + offset[1])
            if check in self.solids:
                solids.append(self.solids[check])
            elif include_gaps and (check in self.gaps):
                solids.append(self.gaps[check])
        return solids
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.get_tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, 
                                         tile['pos'][1] * self.tile_size, 
                                         self.tile_size, 
                                         self.tile_size))
        return rects

    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.block, (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.block, (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            pygame.draw.rect(surf, 'grey', (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size), 1)