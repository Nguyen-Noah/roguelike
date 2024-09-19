import pygame, sys
from pygame.locals import *
from scripts.tilemap import Tilemap
from scripts.config import config

WIDTH = config['window']['base_resolution'][0]
HEIGHT = config['window']['base_resolution'][1]
FPS = config['window']['fps']
dt = 1/FPS
SCALE_RATIO = 3
BASE_RESOLUTION = (WIDTH, HEIGHT)
SCALED_RESOLUTION = config['window']['scaled_resolution']

class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('[Map Editor]')
        self.screen = pygame.display.set_mode(SCALED_RESOLUTION)
        self.display = pygame.Surface(BASE_RESOLUTION)

        self.clock = pygame.time.Clock()

        self.inputs = {
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }

        self.block = pygame.image.load('data/graphics/temp/blank.png')

        self.tilemap = Tilemap(self, tile_size=16)

        self.scroll = [0, 0]

        self.clicking = False
        self.right_clicking = False

    def run(self):
        while True:
            self.display.fill((0, 0, 0))

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll)

            current_tile = self.block.copy()
            current_tile.set_alpha(100)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] / SCALE_RATIO, mouse_pos[1] / SCALE_RATIO)
            tile_pos = (int(mouse_pos[0] + self.scroll[0]) // self.tilemap.tile_size, int(mouse_pos[1] + self.scroll[1]) // self.tilemap.tile_size)
            self.display.blit(current_tile, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))

            if self.clicking:
                self.tilemap.tilemap[f'{tile_pos[0]};{tile_pos[1]}'] = {'type': 'temp', 'variant': 0, 'pos': tile_pos}
            if self.right_clicking:
                tile_loc = f'{tile_pos[0]};{tile_pos[1]}'
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]

            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == 27):
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                if event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.right_clicking = True
                if event.type == MOUSEBUTTONUP:
                    if event.button == 3:
                        self.right_clicking = False
                
                if event.type == KEYDOWN:
                    if event.key == 97:
                        self.inputs['left'] = True
                    if event.key == 100:
                        self.inputs['right'] = True
                    if event.key == 119:
                        self.inputs['up'] = True
                    if event.key == 115:
                        self.inputs['down'] = True

                    if event.key == 111:
                        self.tilemap.save('map.json')

                if event.type == KEYUP:
                    if event.key == 97:
                        self.inputs['left'] = False
                    if event.key == 100:
                        self.inputs['right'] = False
                    if event.key == 119:
                        self.inputs['up'] = False
                    if event.key == 115:
                        self.inputs['down'] = False

            self.screen.blit(pygame.transform.scale(self.display, SCALED_RESOLUTION), (0, 0))
            self.clock.tick(FPS)
            self.display.fill((0, 147, 191))
            pygame.display.update()

editor = Editor()
editor.run()