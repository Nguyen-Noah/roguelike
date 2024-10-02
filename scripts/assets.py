import pygame, os, moderngl
from .spritesheets import load_spritesheets

PATH = 'data/graphics'
SPRITESHEET_PATH = 'data/graphics/spritesheets'

class Assets:
    def __init__(self, game):
        self.game = game
        self.custom_tile_renders = {}

        self.temp = self.load_dir(f'{PATH}/temp')
        self.hair = self.load_dir(f'{PATH}/hair', colorkey=(255, 255, 255))
        self.weapons = self.load_dir(f'{PATH}/weapons')
        self.spritesheets = self.spritesheets = load_spritesheets(self.pg2tex, SPRITESHEET_PATH, colorkey=(255, 255, 255), scale=self.game.window.scale_ratio) if SPRITESHEET_PATH else {}

        self.custom_tile_renderers = {}


    def enable(self, *args, **kwargs):
        pass

    def load_dirs(self, path):
        dirs = {}
        for dir in os.listdir(path):
            dirs[dir] = self.load_dir(path + '/' + dir)
        return dirs

    def load_dir(self, path, colorkey=(0, 0, 0)):
        texture_dir = {}
        for file in os.listdir(path):
            texture_dir[file.split('.')[0]] = self.load_img(path + '/' + file, colorkey=colorkey)
        return texture_dir
    
    def load_img(self, path, colorkey=(0, 0, 0)):
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (img.width * self.game.window.scale_ratio, img.height * self.game.window.scale_ratio))
        img.set_colorkey(colorkey)
        texture = self.pg2tex(img)
        return texture
    
    def pg2tex(self, surf):
        w, h = surf.get_size()
        tex_data = pygame.image.tobytes(surf, 'RGBA', 1)
        tex = self.game.mgl.ctx.texture((w, h), 4, tex_data)
        tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        return tex