import pygame, os

class Assets:
    def __init__(self, game):
        self.game = game

    def load_dirs(self, path):
        dirs = {}
        for dir in os.listdir(path):
            dirs[dir] = self.load_dir(path + '/' + dir)
        return dirs

    def load_dir(self, path):
        image_dir = {}
        for file in os.listdir(path):
            image_dir[file.split('.')[0]] = self.load_img(path + '/' + file, (0, 0, 0))
        return image_dir
    
    def load_img(self, path, colorkey):
        img = pygame.image.load(path).convert_alpha()
        img.set_colorkey(colorkey)
        return img