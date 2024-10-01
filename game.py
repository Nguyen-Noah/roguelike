from scripts.window import Window
from scripts.input import Input
from scripts.renderer import Renderer
from scripts.world import World
from scripts.camera import Camera
from scripts.assets import Assets
from scripts.audio import Audio
from scripts.entity_db import EntityDB
from scripts.entity_groups import EntityGroups

class Game:
    def __init__(self):
        self.window = Window(self)
        self.entity_groups = EntityGroups(self)
        self.entity_db = EntityDB(path='data/graphics/entities')
        self.assets = Assets(self)
        self.input = Input(self)
        self.renderer = Renderer(self)
        self.camera = Camera(self, self.window.resolution)
        self.world = World(self)
        self.audio = Audio()

        self.renderer.set_groups(['default'])

    def update(self):
        self.input.update()
        self.window.render_frame()
        self.world.update()
        self.camera.update()
        self.entity_groups.update()
        self.renderer.cycle({
            'default': self.window.display
            })
        
        print(self.input.holding('down'))

    def run(self):
        while True:
            self.update()

if __name__ == "__main__":
    game = Game()
    game.run()