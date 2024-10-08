import pygame, random
from .quads import Quads
from .utils import write_tjson, read_tjson

ENTITY_MAP = {}
RANDOMIZE_GROUPS = {}

def basic_tile_render(tile, offset=(0, 0), group='default'):
    tile.renderer.blit(tile.img, (tile.raw_pos[0] + tile.offset[0] - offset[0], tile.raw_pos[1] + tile.offset[1] - offset[1]), z=tile.layer, group=group)


class Tile:
    def __init__(self, parent, tile_type, pos, wall=False, variant=None, z_offset=0, overhang=False):
        self.parent = parent
        self.pos = pos
        self.type = tile_type
        self.wall = wall
        self.z_offset = z_offset
        self.overhang = overhang

        self.variant = variant

        if self.type in RANDOMIZE_GROUPS:
            if random.random() < RANDOMIZE_GROUPS[self.type][0]:
                self.variant = (random.randint(0, RANDOMIZE_GROUPS[self.type][1] - 1), self.variant[1] if self.variant[1] else 0)

    @property
    def rect(self):
        return pygame.Rect(self.pos[0] * self.parent.tile_size, self.pos[1] * self.parent.tile_size, self.parent.tile_size, self.parent.tile_size)

    def render(self, offset):
        rpos = ((self.pos[0] * self.parent.game.window.scale_ratio) * self.parent.tile_size[0] - offset[0], (self.pos[1] * self.parent.game.window.scale_ratio) * self.parent.tile_size[1] - offset[1])

        z = -99999
        if self.wall:
            z = self.pos[1] + 1
        z += self.z_offset

        if self.variant:
            img = self.parent.game.assets.spritesheets[self.type]['assets'][self.variant]
        else:
            img = self.parent.game.assets.images['tiles'][self.type]
        
        self.parent.game.renderer.blit(img, rpos, z=z)

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
                    self.insert(Tile(self, tile_data['group'], tile_id=tuple(tile_data['tile_id']), pos=tuple(tile_data['pos']), layer=tile_data['layer'], custom_data=tile_data['c'] if 'c' in tile_data else ''))
        for tile_data in data['offgrid_tiles']['objects'].values():
            if spawn_hook(tile_data, False):
                self.insert(Tile(self, tile_data['group'], tile_id=tuple(tile_data['tile_id']), pos=tuple(tile_data['pos']), layer=tile_data['layer'], custom_data=tile_data['c'] if 'c' in tile_data else ''), ongrid=False, ignore_lock=True)

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
            group_conf = self.game.assets.spritesheets[tile['group']['config']]
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
                    if 'categories' in tile_conf:
                        categories = tile_conf['categories']
                    if 'solid' in categories:
                        self.solids[loc] = Tile(self, tile['group'], loc, variant=tile_id)
                    if 'floor' in categories:
                        # don't overwrite 'backwall' tiles
                        if (loc not in self.floor) and (loc not in self.walls):
                            self.floor[loc] = Tile(self, tile['group'], loc, variant=tile_id)
                    if 'backwall' in categories:
                        self.floor[loc] = Tile(self, tile['group'], loc, variant=tile_id)
                        self.solids[loc] = self.floor[loc]
                        self.minimap_base.set_at(loc, (67, 51, 87))
                    if 'wall' in categories:
                        self.walls[loc] = Tile(self, tile['group'], loc, variant=tile_id, wall=True)
                        self.solids[loc] = self.walls[loc]
                        self.minimap_base.set_at(loc, (67, 51, 87))
                    if 'overhang' in categories:
                        self.walls[loc] = Tile(self, tile['group'], loc, variant=tile_id, wall=True, overhang=True)
                    if 'cliff' in categories:
                        self.floor[loc] = Tile(self, tile['group'], loc, variant=tile_id)
                        self.gaps[loc] = self.floor[loc]
                        self.minimap_base.set_at(loc, (74, 156, 223))
                    if 'spawn' in categories:
                        self.spawn = (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size)
                    if 'respawn' in categories:
                        self.respawn = (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size)
                    if 'exit' in categories:
                        self.exit = (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size)
                    if 'shop' in categories:
                        self.shops.append((tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))
                    if 'weapon' in categories:
                        self.weapon_shops.append((tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))
                    if 'block_decor' in categories:
                        self.decor_block[loc] = True

        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                if not any([(x, y) in section for section in [self.walls, self.solids, self.floor, self.gaps]]):
                    self.gaps[(x, y)] = Tile(self, 'water_wall', (x, y))
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
                    self.floor[(x, y)].render(cam_r.topleft)