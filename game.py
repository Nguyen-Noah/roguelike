from scripts.window import Window
from scripts.input import Input
from scripts.renderer import Renderer
from scripts.world import World
from scripts.assets import Assets

class Game:
    def __init__(self):
        self.window = Window(self)
        self.assets = Assets(self)
        self.input = Input(self)
        self.renderer = Renderer(self)
        self.world = World(self)

    def update(self):
        self.input.update()
        self.window.render_frame()
        self.world.update()
        self.renderer.cycle()

    def run(self):
        while True:
            self.update()

if __name__ == "__main__":
    game = Game()
    game.run()