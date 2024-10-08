import pygame, time
from .config import config
from .mgl.mgl import MGL

class Window:
    def __init__(self, game):
        self.game = game

        pygame.init()

        # screen resolution
        self.resolution = config['window']['resolution']
        self.scale_ratio = config['window']['scale_ratio']
        self.offset = (0, 0)

        # opengl
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        # clock and fps
        self.fps = config['window']['fps']
        self.clock = pygame.time.Clock()
        self.dt = 1 / self.fps
        self.time = 0

        # blitting surfs
        self.screen = pygame.display.set_mode(self.resolution, pygame.OPENGL | pygame.DOUBLEBUF)
        self.display = pygame.Surface(self.resolution)
        self.mgl = MGL()

    def render_frame(self):
        self.mgl.render(self.display, self.time, self.game.input.mouse.pos)
        self.clock.tick(self.fps)
        self.display.fill((0, 0, 0))
        self.time += self.dt