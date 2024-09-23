from scripts.window import Window
from scripts.input import Input
from scripts.renderer import Renderer
from scripts.world import World
from scripts.assets import Assets
from scripts.audio import Audio
from scripts.entity_db import EntityDB

class Game:
    def __init__(self):
        self.window = Window(self)
        self.entity_db = EntityDB(path='data/graphics/entities')
        self.assets = Assets(self)
        self.input = Input(self)
        self.renderer = Renderer(self)
        self.world = World(self)
        self.audio = Audio()

        self.renderer.set_groups(['default', 'subpixel'])

    def update(self):
        self.input.update()
        self.window.render_frame()
        self.world.update()
        self.renderer.cycle({
            'default': self.window.display,
            'subpixel': self.window.s_display
            })

    def run(self):
        while True:
            self.update()

if __name__ == "__main__":
    game = Game()
    game.run()