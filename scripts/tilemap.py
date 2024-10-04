import pygame, random
import numpy as np
from array import array
from .quads import Quads
from .utils import write_tjson, read_tjson

ENTITY_MAP = {}
RANDOMIZE_GROUPS = {}

def basic_tile_render(tile, offset=(0, 0), group='default'):
    tile.renderer.blit(tile.img, (tile.raw_pos[0] + tile.offset[0] - offset[0], tile.raw_pos[1] + tile.offset[1] - offset[1]), z=tile.layer, group=group)

def create_tile_quad(tile_pos, tile_size):
    x, y = tile_pos
    w, h = tile_size

    verticies = [
        x, y, 0.0, 0.0,
        x + w, y, 1.0, 0.0,
        x + w, y + h, 1.0, 1.0,
        x, y + h, 0.0, 1.0
    ]
    return verticies


class Tile:
    def __init__(self, game, tile_type, pos, tile_size=(16, 16), wall=False, variant=None, z_offset=0, program=None):
        self.game = game
        self.pos = pos
        self.type = tile_type
        self.wall = wall
        self.tile_size = tile_size
        self.z_offset = z_offset
        self.program = program

        self.renderer = self.game.mgl.tile
        # since the scale ratio is 3, we'll divide all cartesian x-axes by 3/2 (1.5) and then multiply that by the tilesize, which is 16
        # in order to properly scale things without messing up the texture, only touch the cartesian stuff
        vertices = self.game.mgl.ctx.buffer(array('f', [
            # position (x, y), uv coords (x, y)
            -1.0/(1.5 * 16), 1.0/16, 0.0, 0.0,  # topleft
            1.0/(1.5 * 16), 1.0/16, 1.0, 0.0,   # topright
            -1.0/(1.5 * 16), -1.0/16, 0.0, 1.0, # bottomleft
            1.0/(1.5 * 16), -1.0/16, 1.0, 1.0,  # bottomright
        ]).tobytes())
        self.renderer.vbo = vertices
        self.renderer.create_vao()
        self.variant = variant

        if self.type in RANDOMIZE_GROUPS:
            if random.random() < RANDOMIZE_GROUPS[self.type][0]:
                self.variant = (random.randint(0, RANDOMIZE_GROUPS[self.type][1] - 1), self.variant[1] if self.variant[1] else 0)

    @property
    def rect(self):
        return pygame.Rect(
            self.pos[0] * self.tile_size[0], 
            self.pos[1] * self.tile_size[1], 
            self.tile_size[0], 
            self.tile_size[1]
            )

    def render(self):
        rpos = (
            self.pos[0] * self.tile_size[0],
            self.pos[1] * self.tile_size[1]
        )

        if self.variant:
            texture = self.game.assets.spritesheets[self.type]['assets'][self.variant]
        else:
            texture = self.game.assets.images['tiles'][self.type]

        uniforms = {
            'surface': texture,
            'tile_pos': np.array((random.random(), random.random()), dtype='f4')
        }

        self.renderer.render(uniforms=uniforms)

class Tilemap:
    def __init__(self, game, tile_size=(16, 16), dimensions=(16, 16)):
        self.game = game
        self.tile_size = tile_size
        self.dimensions = tuple(dimensions)
        self.grid_tiles = {}
        self.physics_priority = {'solid': 1.0, 'dropthrough': 0.9, 'rampr': 0.8, 'rampl': 0.7}
        self.dimensions = tuple(dimensions)
        self.dimensional_lock = True
        
        self.load_map('save')

    def physics_gridtile(self, pos):
        grid_pos = (pos[0] // self.tile_size[0], pos[1] // self.tile_size[1])
        if grid_pos in self.physics_map:
            return self.physics_map[grid_pos][0][2]
        return None

    def clear(self):
        self.floor = {}
        self.walls = {}
        self.solids = {}
        self.gaps = {}

    def reset(self):
        self.grid_tiles = {}
        self.physics_map = {}
        self.offgrid_tiles = Quads((self.tile_size[0] + self.tile_size[1]) * 3)
        self.i = 0

    def load(self, path, spawn_hook=lambda tile_data, ongrid: True):
        data = read_tjson(path)
        self.reset()
        self.tile_size = tuple(data['tile_size'])
        self.dimensions = tuple(data['dimensions'])
        for loc in data['grid_tiles']:
            for layer in data['grid_tiles'][loc]:
                tile_data = data['grid_tiles'][loc][layer]
                if spawn_hook(tile_data, True):
                    self.insert(Tile(self.game, tile_data['group'], tile_id=tuple(tile_data['tile_id']), pos=tuple(tile_data['pos']), layer=tile_data['layer'], custom_data=tile_data['c'] if 'c' in tile_data else ''))
        for tile_data in data['offgrid_tiles']['objects'].values():
            if spawn_hook(tile_data, False):
                self.insert(Tile(self.game, tile_data['group'], tile_id=tuple(tile_data['tile_id']), pos=tuple(tile_data['pos']), layer=tile_data['layer'], custom_data=tile_data['c'] if 'c' in tile_data else ''), ongrid=False, ignore_lock=True)

    def load_map(self, map_name):
        self.clear()

        map_data = read_tjson(f'data/maps/{map_name}.pmap')

        self.dimensions = map_data['dimensions']
        self.minimap_base = pygame.Surface(self.dimensions)

        self.wall_map = pygame.Surface(self.dimensions, pygame.SRCALPHA)

        for obj_id in map_data['offgrid_tiles']['objects']:
            tile = map_data['offgrid_tiles']['objects'][obj_id]
            tile_id = tuple(tile['tile_id'])
            img = self.game.assets.spritesheets[tile['group']]['assets'][tile_id]
            group_conf = self.game.assets.spritesheets[tile['group']]['config']
            tile_conf = {}
            if tile_id in group_conf:
                tile_conf = group_conf[tile_id]

            categories = []
            if 'categories' in tile_conf:
                categories = tile_conf['categories']

            if tile['group'] == 'entities':
                if tile_id in ENTITY_MAP:
                    entity = ENTITY_MAP[tile_id][0](ENTITY_MAP[tile_id][1], tile['pos'])
                    self.e['EntityGroups'].add(entity, 'entities')
                
        for loc in map_data['grid_tiles']:
            tile_stack = map_data['grid_tiles'][loc]
            for layer in tile_stack:
                tile = tile_stack[layer]
                group_conf = self.game.assets.spritesheets[tile['group']]['config']
                tile_id = tuple(tile['tile_id'])
                if tile_id in group_conf:
                    tile_conf = group_conf[tile_id]
                    categories = ['floor']

                    #program = self.game.mgl.block_program

                    if 'categories' in tile_conf:
                        categories = tile_conf['categories']
                    if 'solid' in categories:
                        self.solids[loc] = Tile(self.game, tile['group'], loc, variant=tile_id)
                    if 'floor' in categories:
                        # don't overwrite 'backwall' tiles
                        if (loc not in self.floor) and (loc not in self.walls):
                            self.floor[loc] = Tile(self.game, tile['group'], loc, variant=tile_id)

        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                if not any([(x, y) in section for section in [self.walls, self.solids, self.floor, self.gaps]]):
                    self.gaps[(x, y)] = Tile(self.game, 'water_wall', (x, y))
                    self.minimap_base.set_at((x, y), (74, 156, 223))

        # generate wall map
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                if not self.is_open_space((x, y)):
                    self.wall_map.set_at((x, y), (0, 0, 255, 255))

    def is_open_space(self, loc):
        if (loc not in self.solids) and (loc not in self.gaps):
            return True
        return False

    def render(self):
        cam_r = self.game.camera.rect
        tl = (cam_r.left // (self.tile_size[0] * self.game.window.scale_ratio), cam_r.top // (self.tile_size[1] * self.game.window.scale_ratio) - 1)
        br = (cam_r.right // self.tile_size[0], cam_r.bottom // self.tile_size[1])

        for y in range(tl[1], br[1] + 1):
            for x in range(tl[0], br[0] + 1):
                if (x, y) in self.floor:
                    self.floor[(x, y)].render()