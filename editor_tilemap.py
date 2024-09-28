import pygame, json
from scripts.quads import Quads
from scripts.utils import write_tjson, read_tjson

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'temp'}
AUTOTILE_TYPES = {'temp'}
TILES_AROUND = [(0, 0), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 1), (1, 1), (-1, 1)]

def basic_tile_render(tile, offset=(0, 0), group='default'):
    tile.renderer.blit(tile.img, (tile.raw_pos[0] + tile.offset[0] - offset[0], tile.raw_pos[1] + tile.offset[1] - offset[1]), z=tile.layer, group=group)


class Tile:
    def __init__(self, game, group, tile_id=(0, 0), pos=(0, 0), layer=0, custom_data=''):
        self.game = game
        self.group = group
        self.render_func = basic_tile_render
        self.change_id(tile_id)
        self.grid_pos = tuple(pos)
        self.raw_pos = tuple(pos)
        self.layer = layer
        self.rect = pygame.Rect(*pos, *self.img.get_size())
        self.map = None
        self.flags = set(self.config['flags'] if 'flags' in self.config else ['solid'])
        self.physics_type = None
        self.custom_data = custom_data
        
    def render(self, offset=(0, 0), group='default'):
        self.render_func(self, offset=offset, group=group)
    
    def primitive_render(self, surf, offset=(0, 0)):
        surf.blit(self.img, (self.raw_pos[0] + self.offset[0] - offset[0], self.raw_pos[1] + self.offset[1] - offset[1]))
        
    def shift_clone(self, pos):
        return Tile(self.game, self.group, tile_id=self.tile_id, pos=pos, layer=self.layer)

    def change_id(self, tile_id):
        self.tile_id = tile_id
        self.img = self.game.assets.spritesheets[self.group]['assets'][tile_id]
        self.config = self.game.assets.spritesheets[self.group]['config'][tile_id]
        if self.group in self.game.custom_tile_renderers:
            self.render_func = self.game.custom_tile_renderers[self.group]
        self.offset = self.config['offset']
        
    def export(self):
        data = {'group': self.group, 'tile_id': self.tile_id, 'pos': self.grid_pos, 'layer': self.layer}
        if len(self.custom_data):
            data['c'] = self.custom_data
        return data
    
    def attach(self, tilemap, ongrid=True):
        if ongrid:
            self.raw_pos = (self.grid_pos[0] * tilemap.tile_size[0], self.grid_pos[1] * tilemap.tile_size[1])
            self.rect = pygame.Rect(*self.raw_pos, *tilemap.tile_size)
        self.map = tilemap
        for flag in self.flags:
            if flag in tilemap.physics_priority:
                self.physics_type = flag

    def neighbors(self, offsets, handle_edge=False):
        neighbors = {}
        for offset in offsets:
            loc = (self.grid_pos[0] + offset[0], self.grid_pos[1] + offset[1])
            if loc in self.map.grid_tiles:
                if self.layer in self.map.grid_tiles[loc]:
                    neighbors[tuple(offset[:2])] = self.map.grid_tiles[loc][self.layer]
            if handle_edge and (not self.map.in_map(loc)) and self.map.dimensional_lock:
                neighbors[tuple(offset[:2])] = 'edge'
        return neighbors

class Tilemap:
    def __init__(self, game, tile_size=(16, 16), dimensions=(16, 16)):
        self.game = game
        self.tile_size = tile_size
        self.dimensions = tuple(dimensions)
        self.grid_tiles = {}
        self.physics_priority = {'solid': 1.0, 'dropthrough': 0.9, 'rampr': 0.8, 'rampl': 0.7}
        self.dimensions = tuple(dimensions)
        self.dimensional_lock = True
        self.reset()

    def reset(self):
        self.grid_tiles = {}
        self.physics_map = {}
        self.offgrid_tiles = Quads((self.tile_size[0] + self.tile_size[1]) * 3)
        self.i = 0

    def save(self, path):
        output = {'tile_size': self.tile_size, 'grid_tiles': {}, 'offgrid_tiles': self.offgrid_tiles.export(lambda x: x.export()), 'dimensions': self.dimensions}
        for loc in self.grid_tiles:
            output['grid_tiles'][loc] = {}
            for layer in self.grid_tiles[loc]:
                output['grid_tiles'][loc][layer] = self.grid_tiles[loc][layer].export()
        write_tjson(path, output)

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
                self.insert(Tile(tile_data['group'], tile_id=tuple(tile_data['tile_id']), pos=tuple(tile_data['pos']), layer=tile_data['layer'], custom_data=tile_data['c'] if 'c' in tile_data else ''), ongrid=False, ignore_lock=True)

    # could be made faster by using offsets for each tile test instead of a whole area mask
    def optimize_area(self, rect, layer=0):
        masks = self.area_masks(rect)
        layer_ids = sorted(list(masks))
        if layer in masks:
            involved_layers = layer_ids[layer_ids.index(layer) + 1:]
            if len(involved_layers):
                # bitwise OR all layers above together
                combined_mask = masks[involved_layers[0]]
                for top_layer in involved_layers[1:]:
                    combined_mask.draw(masks[top_layer], (0, 0))
                # get map of open space
                combined_mask.invert()
                for loc in self.rect_grid_locs(rect):
                    if loc in self.grid_tiles:
                        if layer in self.grid_tiles[loc]:
                            surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                            tile = self.grid_tiles[loc][layer]
                            tile.primitive_render(surf, offset=rect.topleft)
                            tile_mask = pygame.mask.from_surface(surf)
                            if not tile_mask.overlap_area(combined_mask, (0, 0)):
                                # the tile is not visible
                                self.grid_delete(loc, layer=layer)

    def area_masks(self, rect):
        surfs = {}
        for loc in self.rect_grid_locs(rect):
            if loc in self.grid_tiles:
                layers = self.grid_tiles[loc]
                for layer in layers:
                    if layer not in surfs:
                        surfs[layer] = pygame.Surface(rect.size, pygame.SRCALPHA)
                    tile = layers[layer]
                    tile.primitive_render(surfs[layer], offset=rect.topleft)
        masks = {layer: pygame.mask.from_surface(surfs[layer]) for layer in surfs}
        return masks

    def rect_grid_locs(self, rect):
        topleft = (rect.x // self.tile_size[0], rect.y // self.tile_size[1])
        bottomright = (rect.right // self.tile_size[0], rect.bottom // self.tile_size[1])
        locs = []
        for y in range(topleft[1], bottomright[1] + 1):
            for x in range(topleft[0], bottomright[0] + 1):
                locs.append((x, y))
        return locs

    def count_tiles(self):
        count = {'grid': 0, 'offgrid': len(self.offgrid_tiles.objects)}
        for loc in self.grid_tiles:
            count['grid'] += len(self.grid_tiles[loc])
        return count

    def count_rect_tiles(self, rect):
        layers = self.rect_select(rect)
        count = 0
        for layer in layers:
            count += len(layers[layer])
        return count

    def gridtile(self, pos):
        if pos in self.grid_tiles:
            return self.grid_tiles[pos]
        return {}

    def rect_select(self, rect, gridonly=False):
        topleft = (rect.x // self.tile_size[0], rect.y // self.tile_size[1])
        bottomright = (rect.right // self.tile_size[0], rect.bottom // self.tile_size[1])
        layers = {}
        
        # grab grid tiles
        for y in range(topleft[1], bottomright[1] + 1):
            for x in range(topleft[0], bottomright[0] + 1):
                tiles = self.gridtile((x, y))
                for k, v in tiles.items():
                    if k not in layers:
                        layers[k] = []
                    layers[k].append(v)
                    
        # grab off-grid tiles
        if not gridonly:
            for tile in self.offgrid_tiles.query(rect):
                if tile.layer not in layers:
                    layers[tile.layer] = []
                layers[tile.layer].append(tile)
            
        return layers

    def rect_delete(self, rect, layer=None):
        topleft = (rect.x // self.tile_size[0], rect.y // self.tile_size[1])
        bottomright = (rect.right // self.tile_size[0], rect.bottom // self.tile_size[1])
        
        for y in range(topleft[1], bottomright[1] + 1):
            for x in range(topleft[0], bottomright[0] + 1):
                grid_pos = (x, y)
                if grid_pos in self.grid_tiles:
                    tile_r = pygame.Rect(grid_pos[0] * self.tile_size[0], grid_pos[1] * self.tile_size[1], *self.tile_size)
                    if tile_r.colliderect(rect):
                        if layer != None:
                            if layer in self.grid_tiles[grid_pos]:
                                if grid_pos in self.physics_map:
                                    for tile in self.physics_map[grid_pos].copy():
                                        if tile[1] == self.grid_tiles[grid_pos][layer]:
                                            self.physics_map[grid_pos].remove(tile)
                                            if not len(self.physics_map[grid_pos]):
                                                del self.physics_map[grid_pos]
                                del self.grid_tiles[grid_pos][layer]
                        else:
                            del self.grid_tiles[grid_pos]
                            if grid_pos in self.physics_map:
                                del self.physics_map[grid_pos]
                        
        tiles = self.offgrid_tiles.query(rect)
        if layer != None:
            for tile in tiles:
                if tile.layer == layer:
                    if tile.rect.colliderect(rect):
                        self.offgrid_tiles.delete(tile)
        else:
            for tile in tiles:
                if tile.rect.colliderect(rect):
                    self.offgrid_tiles.delete(tile)

    def in_map(self, gridpos):
        dimensions_r = pygame.Rect(0, 0, *self.dimensions)
        return dimensions_r.collidepoint(gridpos)

    def floodfill(self, tile):
        check_locs = set((tile.grid_pos,))
        fill_locs = set()
        borders = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        checks = 0
        while len(check_locs):
            for loc in check_locs.copy():
                valid = True
                if loc in self.grid_tiles:
                    if tile.layer in self.grid_tiles[loc]:
                        valid = False
                if not self.in_map(loc):
                    valid = False
                if valid:
                    fill_locs.add(loc)
                    for border in borders:
                        check_loc = (loc[0] + border[0], loc[1] + border[1])
                        if check_loc not in fill_locs:
                            check_locs.add(check_loc)
                check_locs.remove(loc)
                checks += 1
                if len(fill_locs) > 2048:
                    return
        for loc in fill_locs:
            self.insert(tile.shift_clone(loc))

    def render_prep(self, rect, offset=(0, 0), group='default'):
        topleft = (rect.x // self.tile_size[0], rect.y // self.tile_size[1])
        bottomright = (rect.right // self.tile_size[0], rect.bottom // self.tile_size[1])
        layers = {}
        
        blits = []
        
        # grab grid tiles
        for y in range(topleft[1], bottomright[1] + 1):
            for x in range(topleft[0], bottomright[0] + 1):
                tiles = self.gridtile((x, y))
                for tile in tiles.values():
                    blits.append((tile.img, (tile.raw_pos[0] + tile.offset[0] - offset[0], tile.raw_pos[1] + tile.offset[1] - offset[1]), tile.layer, group))
                    
        # grab off-grid tiles
        for tile in self.offgrid_tiles.query(rect):
            blits.append((tile.img, (tile.raw_pos[0] + tile.offset[0] - offset[0], tile.raw_pos[1] + tile.offset[1] - offset[1]), tile.layer, group))
        
        return blits

    def visible_layer_contains(self, rect, layer):
        tile_types = set()
        layers = self.rect_select(rect)
        if layer in layers:
            for tile in layers[layer]:
                tile_types.add(tile.group)
        return tile_types

    def insert(self, tile, ongrid=True, ignore_lock=False):
        tile.attach(self, ongrid=ongrid)
        dimensions_r = pygame.Rect(0, 0, *self.dimensions)
        lock = self.dimensional_lock if (not ignore_lock) else False
        if ongrid:
            if lock and (not dimensions_r.collidepoint(tile.grid_pos)):
                return
            if tile.grid_pos not in self.grid_tiles:
                self.grid_tiles[tile.grid_pos] = {}
            self.grid_tiles[tile.grid_pos][tile.layer] = tile
            if tile.physics_type:
                if tile.grid_pos not in self.physics_map:
                    self.physics_map[tile.grid_pos] = []
                self.physics_map[tile.grid_pos].append((self.physics_priority[tile.physics_type], self.i, tile))
                self.physics_map[tile.grid_pos].sort(reverse=True)
                self.i += 1
        else:
            pos = (tile.raw_pos[0] / self.tile_size[0], tile.raw_pos[1] / self.tile_size[1])
            if lock and (not dimensions_r.collidepoint(pos)):
                return
            self.offgrid_tiles.add_raw(tile, tile.rect, tag=True)
        return True

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